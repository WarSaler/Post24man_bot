import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

from ..config import config

class SheetsDatabase:
    def __init__(self):
        # Путь к файлу с учетными данными
        credentials_path = os.path.join(os.path.dirname(__file__), '..', 'credentials', 'credentials.json')
        
        # Области доступа
        scope = ["https://spreadsheets.google.com/feeds", 
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive.file", 
                "https://www.googleapis.com/auth/drive"]
        
        # Авторизация с помощью учетных данных
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
            self.client = gspread.authorize(creds)
            
            # Получаем или создаем таблицу
            try:
                self.sheet = self.client.open(config.GOOGLE_SHEET_NAME)
            except gspread.exceptions.SpreadsheetNotFound:
                # Создаем новую таблицу, если она не существует
                self.sheet = self.client.create(config.GOOGLE_SHEET_NAME)
                # Открываем доступ по email из конфига
                if config.SHARE_EMAIL:
                    self.sheet.share(config.SHARE_EMAIL, perm_type='user', role='writer')
            
            # Проверяем, есть ли лист "news_articles", если нет - создаем
            try:
                self.worksheet = self.sheet.worksheet("news_articles")
            except gspread.exceptions.WorksheetNotFound:
                self.worksheet = self.sheet.add_worksheet(title="news_articles", rows="1000", cols="9")
                # Добавляем заголовки
                headers = [
                    "id", "source_group", "source_message_id", "original_content",
                    "processed_content", "is_approved", "is_posted", "created_at", "posted_at"
                ]
                self.worksheet.append_row(headers)
                
        except Exception as e:
            print(f"Ошибка при инициализации базы данных Google Sheets: {e}")
            self.client = None
            self.sheet = None
            self.worksheet = None
            
    def _get_next_id(self):
        """Получение следующего ID для новой записи"""
        try:
            # Получаем все данные из таблицы
            data = self.worksheet.get_all_values()
            if len(data) <= 1:  # Только заголовки или пусто
                return 1
                
            # Получаем последнюю запись
            last_id = data[-1][0]  # ID находится в первой колонке
            if last_id.isdigit():
                return int(last_id) + 1
            return 1
        except Exception as e:
            print(f"Ошибка при получении следующего ID: {e}")
            return 1
            
    def _row_to_dict(self, row):
        """Преобразование строки таблицы в словарь"""
        if not row:
            return None
            
        try:
            headers = self.worksheet.row_values(1)  # Получаем заголовки
            return dict(zip(headers, row))
        except Exception as e:
            print(f"Ошибка при преобразовании строки в словарь: {e}")
            return None
    
    def add_news_article(self, source_group, original_content, source_message_id=None):
        """Добавление новой статьи"""
        try:
            if not self.worksheet:
                print("Таблица не инициализирована")
                return None
                
            # Получаем следующий ID
            article_id = self._get_next_id()
            
            # Формируем данные для добавления
            row_data = [
                article_id,                    # id
                source_group,                  # source_group
                source_message_id or "",       # source_message_id
                original_content,              # original_content
                "",                            # processed_content
                "FALSE",                       # is_approved
                "FALSE",                       # is_posted
                datetime.utcnow().isoformat(), # created_at
                ""                             # posted_at
            ]
            
            # Добавляем строку в таблицу
            self.worksheet.append_row([str(item) for item in row_data])
            return article_id
            
        except Exception as e:
            print(f"Ошибка при добавлении статьи: {e}")
            return None
    
    def update_processed_content(self, article_id, processed_content):
        """Обновление обработанного контента статьи"""
        try:
            if not self.worksheet:
                return False
                
            # Находим строку с указанным ID
            cell = self.worksheet.find(str(article_id), in_column=1)
            if not cell:
                return False
                
            # Обновляем содержимое (колонка processed_content - 5)
            self.worksheet.update_cell(cell.row, 5, processed_content)
            return True
            
        except Exception as e:
            print(f"Ошибка при обновлении обработанного контента: {e}")
            return False
            
    def approve_article(self, article_id):
        """Одобрение статьи"""
        try:
            if not self.worksheet:
                return False
                
            # Находим строку с указанным ID
            cell = self.worksheet.find(str(article_id), in_column=1)
            if not cell:
                return False
                
            # Обновляем флаг is_approved (колонка 6)
            self.worksheet.update_cell(cell.row, 6, "TRUE")
            return True
            
        except Exception as e:
            print(f"Ошибка при одобрении статьи: {e}")
            return False
            
    def mark_as_posted(self, article_id):
        """Отметка статьи как опубликованной"""
        try:
            if not self.worksheet:
                return False
                
            # Находим строку с указанным ID
            cell = self.worksheet.find(str(article_id), in_column=1)
            if not cell:
                return False
                
            # Обновляем флаг is_posted и posted_at
            self.worksheet.update_cell(cell.row, 7, "TRUE")  # is_posted
            self.worksheet.update_cell(cell.row, 9, datetime.utcnow().isoformat())  # posted_at
            return True
            
        except Exception as e:
            print(f"Ошибка при отметке статьи как опубликованной: {e}")
            return False
            
    def get_pending_articles(self, limit=10):
        """Получение статей, ожидающих одобрения"""
        try:
            if not self.worksheet:
                return []
                
            # Получаем все данные из таблицы
            all_data = self.worksheet.get_all_values()
            if len(all_data) <= 1:  # Только заголовки
                return []
                
            # Создаем DataFrame для удобной фильтрации
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            
            # Фильтруем записи с is_approved=FALSE и непустым processed_content
            pending_df = df[
                (df['is_approved'] == "FALSE") & 
                (df['processed_content'] != "")
            ]
            
            # Сортируем по дате создания (по убыванию)
            pending_df = pending_df.sort_values(by='created_at', ascending=False)
            
            # Ограничиваем количество результатов
            pending_df = pending_df.head(limit)
            
            # Формируем результат
            result = []
            for _, row in pending_df.iterrows():
                result.append((
                    int(row['id']),
                    row['source_group'],
                    row['original_content'],
                    row['processed_content']
                ))
            
            return result
            
        except Exception as e:
            print(f"Ошибка при получении статей, ожидающих одобрения: {e}")
            return []
            
    def get_approved_not_posted_articles(self, limit=5):
        """Получение одобренных, но не опубликованных статей"""
        try:
            if not self.worksheet:
                return []
                
            # Получаем все данные из таблицы
            all_data = self.worksheet.get_all_values()
            if len(all_data) <= 1:  # Только заголовки
                return []
                
            # Создаем DataFrame для удобной фильтрации
            df = pd.DataFrame(all_data[1:], columns=all_data[0])
            
            # Фильтруем записи с is_approved=TRUE и is_posted=FALSE
            approved_df = df[
                (df['is_approved'] == "TRUE") & 
                (df['is_posted'] == "FALSE")
            ]
            
            # Сортируем по дате создания (по возрастанию)
            approved_df = approved_df.sort_values(by='created_at', ascending=True)
            
            # Ограничиваем количество результатов
            approved_df = approved_df.head(limit)
            
            # Формируем результат
            result = []
            for _, row in approved_df.iterrows():
                result.append((
                    int(row['id']),
                    row['processed_content']
                ))
            
            return result
            
        except Exception as e:
            print(f"Ошибка при получении одобренных, но не опубликованных статей: {e}")
            return []
            
    def get_article_by_id(self, article_id):
        """Получение статьи по ID"""
        try:
            if not self.worksheet:
                return None
                
            # Находим строку с указанным ID
            cell = self.worksheet.find(str(article_id), in_column=1)
            if not cell:
                return None
                
            # Получаем всю строку
            row_data = self.worksheet.row_values(cell.row)
            
            # Формируем результат
            headers = self.worksheet.row_values(1)
            article = dict(zip(headers, row_data))
            
            return {
                "id": int(article.get("id", 0)),
                "source_group": article.get("source_group", ""),
                "original_content": article.get("original_content", ""),
                "processed_content": article.get("processed_content", ""),
                "is_approved": article.get("is_approved", "FALSE") == "TRUE",
                "is_posted": article.get("is_posted", "FALSE") == "TRUE",
                "created_at": article.get("created_at", "")
            }
            
        except Exception as e:
            print(f"Ошибка при получении статьи по ID: {e}")
            return None

# Создание экземпляра базы данных
db = SheetsDatabase() 
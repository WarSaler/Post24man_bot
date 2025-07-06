from telethon import TelegramClient, events
from telethon.tl.types import Channel, User
from loguru import logger
import asyncio
from datetime import datetime, timedelta

from .config import config
from .db import db
from .gemini_helper import gemini_helper

class NewsParser:
    def __init__(self):
        # Проверяем, настроены ли обязательные параметры
        if not config.TELEGRAM_API_ID or not config.TELEGRAM_API_HASH:
            logger.error("Необходимо указать TELEGRAM_API_ID и TELEGRAM_API_HASH в .env файле")
            raise ValueError("TELEGRAM_API_ID и TELEGRAM_API_HASH не заданы")
        
        # Создаем клиент Telethon для работы с Telegram API
        self.client = TelegramClient('news_parser_session', 
                                    config.TELEGRAM_API_ID,
                                    config.TELEGRAM_API_HASH)
    
    async def start(self):
        """Запускает клиент Telethon"""
        await self.client.start()
        logger.info("Telegram клиент запущен")
        
        # Информация о пользователе
        me = await self.client.get_me()
        logger.info(f"Авторизован как: {me.first_name} (@{me.username})")
    
    async def fetch_recent_messages(self, group_name, hours_ago=24):
        """
        Получает сообщения из указанной группы за последние N часов
        
        Args:
            group_name (str): Название группы (например, @group_name)
            hours_ago (int): Количество часов назад для поиска сообщений
        
        Returns:
            list: Список найденных сообщений
        """
        try:
            entity = await self.client.get_entity(group_name)
            
            # Определяем время для фильтрации сообщений
            since_time = datetime.now() - timedelta(hours=hours_ago)
            
            # Получаем сообщения из группы
            messages = await self.client.get_messages(
                entity=entity,
                limit=20,  # ограничиваем количество сообщений
                offset_date=since_time
            )
            
            logger.info(f"Получено {len(messages)} сообщений из {group_name}")
            return messages
            
        except Exception as e:
            logger.error(f"Ошибка при получении сообщений из {group_name}: {e}")
            return []
    
    async def process_message(self, message, source_group):
        """
        Обрабатывает отдельное сообщение и сохраняет его в базу данных
        
        Args:
            message: Объект сообщения из Telethon
            source_group (str): Название исходной группы
        """
        try:
            # Проверяем, есть ли текст в сообщении
            if not message.text:
                return
            
            # Проверяем минимальную длину сообщения (чтобы не обрабатывать короткие сообщения)
            if len(message.text.strip()) < 50:
                return
            
            # Сохраняем оригинальное сообщение в базу данных
            article_id = db.add_news_article(
                source_group=source_group,
                original_content=message.text,
                source_message_id=message.id
            )
            
            # Перефразируем контент с помощью Gemini
            processed_content = await gemini_helper.rewrite_content(message.text)
            
            # Обновляем обработанный контент в базе данных
            db.update_processed_content(article_id, processed_content)
            
            logger.info(f"Сообщение ID {message.id} из {source_group} успешно обработано (ID статьи: {article_id})")
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения из {source_group}: {e}")
    
    async def parse_all_sources(self):
        """
        Парсит все источники новостей, указанные в конфигурации
        """
        if not config.SOURCE_GROUPS:
            logger.warning("Список SOURCE_GROUPS пуст. Нет источников для парсинга.")
            return
        
        for group in config.SOURCE_GROUPS:
            logger.info(f"Начинаем парсинг группы {group}")
            messages = await self.fetch_recent_messages(group)
            
            # Обрабатываем каждое сообщение
            for message in messages:
                await self.process_message(message, group)
            
            # Небольшая пауза между обработкой разных групп
            await asyncio.sleep(5)
    
    async def run_periodic_parsing(self):
        """
        Запускает периодический парсинг источников
        """
        while True:
            try:
                logger.info("Начинаем плановый парсинг источников")
                await self.parse_all_sources()
                
                # Ждем заданный интервал перед следующим парсингом
                interval_seconds = config.PARSING_INTERVAL_MINUTES * 60
                logger.info(f"Следующий парсинг через {config.PARSING_INTERVAL_MINUTES} минут")
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                logger.error(f"Ошибка при выполнении периодического парсинга: {e}")
                # В случае ошибки делаем паузу перед повторной попыткой
                await asyncio.sleep(300)  # 5 минут
    
    async def stop(self):
        """Останавливает клиент Telethon"""
        await self.client.disconnect()
        logger.info("Telegram клиент остановлен")

# Создание экземпляра парсера новостей
news_parser = NewsParser() 
import google.generativeai as genai
from loguru import logger
from .config import config

class GeminiHelper:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        if not self.api_key:
            logger.error("GEMINI_API_KEY не задан в .env файле")
            raise ValueError("GEMINI_API_KEY не задан")
        
        # Инициализация API ключа
        genai.configure(api_key=self.api_key)
        
        # Получение модели для генерации текста
        self.model = genai.GenerativeModel('gemini-pro')

    async def rewrite_content(self, original_content: str) -> str:
        """
        Перефразирует содержимое новости с помощью Gemini API
        
        Args:
            original_content (str): Исходный текст новости
        
        Returns:
            str: Перефразированный текст новости
        """
        try:
            # Ограничиваем длину входного текста
            if len(original_content) > config.MAX_CONTENT_LENGTH:
                original_content = original_content[:config.MAX_CONTENT_LENGTH] + "..."
            
            # Составляем инструкцию для модели
            prompt = f"""
            Ниже приведен текст новости, который нужно перефразировать для публикации в телеграм-канале о Турции (регион Алания и Газипаша).
            Сохрани всю важную информацию, но измени формулировки, чтобы избежать проблем с авторским правом.
            Текст должен быть легко читаемым, с хорошим форматированием для Telegram.
            Добавь эмодзи для улучшения восприятия.
            Не добавляй от себя фактов, которых нет в исходном тексте.
            
            Исходный текст:
            ```
            {original_content}
            ```
            """
            
            # Генерация перефразированного текста
            response = await self.model.generate_content_async(prompt)
            
            if response.text:
                return response.text.strip()
            else:
                logger.warning("Gemini вернул пустой ответ")
                return "Не удалось перефразировать текст. Пожалуйста, проверьте исходный контент."
                
        except Exception as e:
            logger.error(f"Ошибка при перефразировании контента: {e}")
            return f"Ошибка при обработке контента: {str(e)[:100]}..."

# Создание экземпляра помощника Gemini
gemini_helper = GeminiHelper() 
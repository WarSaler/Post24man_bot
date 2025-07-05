import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Загрузка переменных окружения из .env файла
load_dotenv()

class Config(BaseModel):
    # Telegram Bot токены и настройки
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_USER_IDS: list[int] = [int(id.strip()) for id in os.getenv("ADMIN_USER_IDS", "").split(",") if id.strip()]
    TARGET_GROUP_ID: int = int(os.getenv("TARGET_GROUP_ID", "0"))
    
    # Настройки для Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Настройки для Telethon (парсинг групп)
    TELEGRAM_API_ID: int = int(os.getenv("TELEGRAM_API_ID", "0"))
    TELEGRAM_API_HASH: str = os.getenv("TELEGRAM_API_HASH", "")
    
    # Список групп для парсинга новостей
    SOURCE_GROUPS: list[str] = [group.strip() for group in os.getenv("SOURCE_GROUPS", "").split(",") if group.strip()]
    
    # Настройки базы данных
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./bot_data.db")
    
    # Настройки для регулярного парсинга
    PARSING_INTERVAL_MINUTES: int = int(os.getenv("PARSING_INTERVAL_MINUTES", "60"))
    
    # Максимальное количество символов для обработки Gemini
    MAX_CONTENT_LENGTH: int = 2000

# Создание экземпляра конфигурации
config = Config() 
from ..config import config

# Импортируем только Google Sheets
try:
    from .sheets_database import db as sheets_db
except ImportError:
    sheets_db = None

def get_db():
    """
    Функция возвращает экземпляр базы данных Google Sheets
    """
    if sheets_db is not None:
        print("Используется Google Sheets в качестве базы данных")
        return sheets_db
    else:
        raise ImportError("Не удалось импортировать модуль Google Sheets")

# Экспортируем экземпляр базы данных
db = get_db() 
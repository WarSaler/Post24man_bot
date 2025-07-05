from ..config import config

# Импортируем классы баз данных
try:
    from .database import db as sql_db
except ImportError:
    sql_db = None

try:
    from .sheets_database import db as sheets_db
except ImportError:
    sheets_db = None

def get_db():
    """
    Функция возвращает экземпляр базы данных в зависимости от конфигурации
    """
    if config.USE_GOOGLE_SHEETS and sheets_db is not None:
        print("Используется Google Sheets в качестве базы данных")
        return sheets_db
    else:
        print("Используется SQL база данных")
        return sql_db

# Экспортируем экземпляр базы данных
db = get_db() 
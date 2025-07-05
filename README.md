# Post24man Bot

Telegram-бот для автоматического сбора, перефразирования и публикации новостей о Турции (регионы Алания и Газипаша).

## Функциональность

- Парсинг новостей из указанных Telegram-каналов
- Перефразирование контента с помощью Google Gemini API
- Модерация новостей администратором бота
- Автоматическая публикация одобренных новостей в целевой группе
- Интеграция с n8n для автоматизации процессов
- Хранение данных в Google Sheets

## Требования

- Python 3.10+
- API ключ для Google Gemini
- Токен Telegram Bot API (от [@BotFather](https://t.me/BotFather))
- API ID и API Hash для Telethon (от [my.telegram.org](https://my.telegram.org))
- Ключ сервисного аккаунта Google (credentials.json)
- Docker и Docker Compose для контейнеризации (опционально)

## Установка и настройка

### Локальная установка

1. Клонировать репозиторий:
```bash
git clone https://github.com/yourusername/Post24man_bot.git
cd Post24man_bot
```

2. Создать и активировать виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
# или
venv\Scripts\activate  # Для Windows
```

3. Установить зависимости:
```bash
pip install -r requirements.txt
```

4. Создать файл `.env` со следующими параметрами:
```
# Telegram Bot токены и настройки
BOT_TOKEN=your_bot_token
ADMIN_USER_IDS=123456789,987654321
TARGET_GROUP_ID=-1001234567890

# Настройки для Google Gemini API
GEMINI_API_KEY=your_gemini_api_key

# Настройки для Telethon (парсинг групп)
TELEGRAM_API_ID=12345
TELEGRAM_API_HASH=your_telegram_api_hash

# Список групп для парсинга новостей
SOURCE_GROUPS=@group1,@group2,@group3

# Настройки для Google Sheets
GOOGLE_SHEET_NAME=Post24man_Data
SHARE_EMAIL=your_email@example.com

# Настройки для регулярного парсинга
PARSING_INTERVAL_MINUTES=60
```

5. Настройка Google Sheets:
   - Создайте сервисный аккаунт в [Google Cloud Console](https://console.cloud.google.com/)
   - Включите API Google Sheets и Google Drive
   - Загрузите ключ JSON (credentials.json) и поместите его в папку `bot/credentials/`
   - Укажите название таблицы в `GOOGLE_SHEET_NAME` и email для доступа в `SHARE_EMAIL`

6. Запустить бота:
```bash
python run_bot.py
```

### Запуск через Docker

1. Создать файл `.env` как описано выше.

2. Запустить с помощью Docker Compose:
```bash
docker-compose up -d
```

## Настройка n8n

1. После запуска Docker Compose, откройте n8n по адресу: [http://localhost:5678](http://localhost:5678)

2. Создайте рабочий процесс для интеграции с ботом.

## Структура проекта

```
Post24man_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py            # Основная точка входа
│   ├── config.py          # Конфигурация и переменные окружения
│   ├── news_parser.py     # Парсинг новостей из других групп
│   ├── gemini_helper.py   # Интеграция с Google Gemini API
│   ├── message_handler.py # Обработка сообщений
│   ├── credentials/       # Директория для ключей Google API
│   └── db/
│       ├── __init__.py
│       ├── sheets_database.py # Работа с Google Sheets
│       └── db_factory.py  # Фабрика для базы данных
├── requirements.txt       # Зависимости проекта
├── Dockerfile             # Для запуска на Render
├── docker-compose.yml     # Для локального тестирования
└── n8n/
    └── workflows/         # Файлы воркфлоу для n8n
```

## Команды бота

- `/start` - Запуск бота
- `/help` - Справка по боту
- `/pending` - Показать ожидающие одобрения новости (для администраторов)
- `/approved` - Показать одобренные, но неопубликованные новости (для администраторов)
- `/run_parser` - Запустить парсинг новостей вручную (для администраторов)
- `/status` - Показать статус работы бота (для администраторов)

## Развертывание на Render

1. Создайте новый Web Service на [Render](https://render.com/).
2. Подключите свой GitHub репозиторий.
3. Выберите тип "Docker".
4. Добавьте переменные окружения из файла `.env`.
5. Добавьте переменную `GOOGLE_CREDENTIALS` с содержимым файла credentials.json (в формате Base64).
   Для конвертации файла в Base64 используйте:
   ```
   cat bot/credentials/credentials.json | base64
   ```
6. Нажмите "Create Web Service".

## Лицензия

MIT 
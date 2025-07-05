# Post24man Bot

Telegram-бот для автоматического сбора, перефразирования и публикации новостей о Турции (регионы Алания и Газипаша).

## Функциональность

- Парсинг новостей из указанных Telegram-каналов
- Перефразирование контента с помощью Google Gemini API
- Модерация новостей администратором бота
- Автоматическая публикация одобренных новостей в целевой группе
- Интеграция с n8n для автоматизации процессов

## Требования

- Python 3.10+
- API ключ для Google Gemini
- Токен Telegram Bot API (от [@BotFather](https://t.me/BotFather))
- API ID и API Hash для Telethon (от [my.telegram.org](https://my.telegram.org))
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

4. Создать файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
# Заполните необходимые параметры в .env файле
```

5. Запустить бота:
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
│   └── db/
│       ├── __init__.py
│       └── database.py    # Работа с базой данных
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
5. Нажмите "Create Web Service".

## Лицензия

MIT 
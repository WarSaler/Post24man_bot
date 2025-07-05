FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя с ограниченными правами
RUN adduser --disabled-password --gecos "" appuser
USER appuser

# Создаем том для данных
VOLUME /app/data

# Запускаем бота
CMD ["python", "run_bot.py"] 
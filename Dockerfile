FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директорию для учетных данных Google
RUN mkdir -p /app/bot/credentials

# Добавляем скрипт для декодирования учетных данных Google с улучшенной обработкой
RUN echo '#!/bin/sh\n\
if [ -n "$GOOGLE_CREDENTIALS" ]; then\n\
  # Удаляем любые переносы строк в base64\n\
  CLEANED_CREDS=$(echo "$GOOGLE_CREDENTIALS" | tr -d "\\n\\r")\n\
  # Декодируем очищенную строку\n\
  echo "$CLEANED_CREDS" | base64 -d > /app/bot/credentials/credentials.json\n\
  echo "Учетные данные Google сохранены"\n\
fi\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Создаем пользователя с ограниченными правами
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app/bot/credentials
USER appuser

# Создаем том для данных
VOLUME /app/data

# Запускаем бота через entrypoint скрипт
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "run_bot.py"] 
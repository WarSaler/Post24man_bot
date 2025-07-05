import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from loguru import logger

from .config import config
from .message_handler import router as message_router
from .news_parser import news_parser

# Настройка логирования
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("bot_logs.log", rotation="10 MB", level="DEBUG", compression="zip")

# Создаем экземпляр бота
bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)

# Создаем диспетчер
dp = Dispatcher()

# Регистрируем роутеры
dp.include_router(message_router)

# Функция для отправки сообщения в целевую группу
async def send_message_to_group(text: str):
    """
    Отправляет сообщение в целевую группу
    
    Args:
        text (str): Текст сообщения
    """
    try:
        await bot.send_message(
            chat_id=config.TARGET_GROUP_ID,
            text=text,
            parse_mode=ParseMode.HTML
        )
        logger.info(f"Сообщение успешно отправлено в группу {config.TARGET_GROUP_ID}")
        return True
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения в группу: {e}")
        return False

# Функция для публикации одобренных новостей
async def publish_approved_news():
    """
    Публикует одобренные новости в целевую группу
    """
    from .db.database import db
    
    while True:
        try:
            # Получаем одобренные, но неопубликованные новости
            articles = db.get_approved_not_posted_articles(limit=1)
            
            if articles:
                # Публикуем каждую новость
                for article_id, content in articles:
                    success = await send_message_to_group(content)
                    
                    if success:
                        # Отмечаем новость как опубликованную
                        db.mark_as_posted(article_id)
                        logger.info(f"Новость ID {article_id} успешно опубликована")
                    else:
                        logger.error(f"Не удалось опубликовать новость ID {article_id}")
                    
                    # Делаем небольшую паузу между публикациями
                    await asyncio.sleep(5)
            
            # Ждем 30 минут до следующей проверки
            await asyncio.sleep(30 * 60)
        
        except Exception as e:
            logger.error(f"Ошибка в процессе публикации новостей: {e}")
            await asyncio.sleep(300)  # 5 минут

# Функция для настройки команд бота
async def set_bot_commands():
    """
    Настраивает команды бота для меню
    """
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Справка по боту"),
        BotCommand(command="pending", description="Показать ожидающие новости"),
        BotCommand(command="approved", description="Показать одобренные новости"),
        BotCommand(command="run_parser", description="Запустить парсинг"),
        BotCommand(command="status", description="Статус работы бота"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Команды бота настроены")

# Функция для запуска ручного парсинга новостей
async def manual_parse_news():
    """
    Запускает процесс парсинга новостей вручную
    """
    try:
        await news_parser.parse_all_sources()
        logger.info("Ручной парсинг новостей завершен")
        return True
    except Exception as e:
        logger.error(f"Ошибка при ручном парсинге новостей: {e}")
        return False

# Основная функция для запуска бота
async def main():
    """
    Основная функция для запуска бота
    """
    try:
        # Настраиваем команды бота
        await set_bot_commands()
        
        # Запускаем парсер новостей
        await news_parser.start()
        
        # Запускаем задачи в фоновом режиме
        asyncio.create_task(news_parser.run_periodic_parsing())
        asyncio.create_task(publish_approved_news())
        
        # Запускаем бота
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    finally:
        # Останавливаем парсер новостей
        await news_parser.stop()
        
        # Закрываем сессию бота
        await bot.session.close()
        logger.info("Бот остановлен")

# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен по команде пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 
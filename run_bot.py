#!/usr/bin/env python
"""
Точка входа для запуска бота
"""
import asyncio
import sys
from loguru import logger

if __name__ == "__main__":
    try:
        from bot.main import main
        asyncio.run(main())
    except ImportError as e:
        print(f"Ошибка импорта: {e}. Убедитесь, что все зависимости установлены.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Бот остановлен по команде пользователя")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1) 
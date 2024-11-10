import asyncio
import logging
from aiogram import Bot, Dispatcher
from bot.db import init_db
from bot.logic import standard_handler_router
from config.settings import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info("Инициализация бота")
    async with Bot(token=BOT_TOKEN) as bot:
        dp = Dispatcher()
        dp.include_router(standard_handler_router)
        logger.info("Роутеры добавлены в диспетчер")

        await init_db()
        logger.info("База данных инициализирована")

        # Запуск polling
        logger.info("Запуск polling")
        await dp.start_polling(bot)
        logger.info("Polling завершен")

# Запуск бота
if __name__ == "__main__":
    try:
        logger.info("Запуск основного цикла")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Бот был остановлен вручную")
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}")

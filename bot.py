import asyncio
import os
import signal
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from core.handlers.start import router as start_router
from core.handlers.vin import router as vin_router
from core.logging.logger import logger
from core.utils.global_configs import PARSE_MODE

# Извлечение токена из .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError('BOT_TOKEN не найден в .env!')


# LIFESPAN-менеджер, выполнит команды ДО и ПОСЛЕ polling автоматически
@asynccontextmanager
async def lifespan(bot: Bot):
    """Lifespan-менеджер."""

    logger.info('Запуск бота...')
    yield
    logger.info('Остановка бота...')
    await bot.session.close()


async def main() -> None:
    """Основная функция бота."""

    def signal_handler(signum, frame):
        """Обработка Ctrl + C."""

        logger.info(f'Получен сигнал {signum}, завершение...')
        loop.stop()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler, sig, None)

    bot =  Bot(
        token=TOKEN,
        default=DefaultBotProperties(parse_mode=PARSE_MODE),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.include_routers(start_router, vin_router)

    try:
        await dp.start_polling(bot, lifespan=lifespan(bot))
    finally:
        logger.info('Бот полностью остановлен.')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info('Бот остановлен пользователем')
    except Exception as e:
        logger.critical(f'Критическая ошибка: {e}')

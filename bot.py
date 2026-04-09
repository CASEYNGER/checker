"""
Точка входа в Telegram-бота.

Модуль отвечает за:
- загрузку переменных окружения;
- инициализацию экземпляра Bot и Dispatcher;
- подключение роутеров;
- запуск polling;
- корректное завершение работы бота по сигналам SIGINT/SIGTERM.

Используемые роутеры:
- start_router: стартовые команды и справочная информация;
- vin_router: обработка VIN и выдача результата проверки.
"""

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
from core.middlewares.rate_limit import RateLimitMiddleware
from core.utils.global_configs import PARSE_MODE, OWNER_ID

# Загружаем переменные окружения из .env
load_dotenv()

# Извлекаем токен Telegram-бота из окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError('BOT_TOKEN не найден в .env!')


@asynccontextmanager
async def lifespan(bot: Bot):
    """
    Lifespan-менеджер жизненного цикла бота.

    Выполняет действия:
    - до запуска polling - логирует старт приложения;
    - после завершения polling - логирует остановку и закрывает HTTP-сессию бота.

    :param bot:
        Экземпляр aiogram.Bot, для которого нужно корректно закрыть сессию.
    :yield:
        Управление передаётся основному процессу polling.
    """

    logger.info('Запуск бота...')
    yield
    logger.info('Остановка бота...')
    await bot.session.close()


async def main() -> None:
    """
    Основная асинхронная функция запуска Telegram-бота.

    Выполняет:
    1. Регистрацию обработчиков системных сигналов SIGINT и SIGTERM.
    2. Создание экземпляра Bot с глобальным parse mode.
    3. Инициализацию in-memory хранилища FSM.
    4. Создание Dispatcher.
    5. Подключение роутеров.
    6. Запуск polling.

    :return:
        Ничего не возвращает.
    """

    def signal_handler(signum, frame):
        """
        Обработчик системных сигналов завершения.

        Используется для логирования получения сигнала и остановки event loop.

        :param signum:
            Номер полученного сигнала.
        :param frame:
            Текущий стековый фрейм (не используется напрямую).
        """

        logger.info(f'Получен сигнал {signum}, завершение...')
        loop.stop()

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler, sig, None)

    bot =  Bot(
        token=TOKEN,
        default=DefaultBotProperties(
            parse_mode=PARSE_MODE
        ),
    )
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    vin_router.message.middleware(
        RateLimitMiddleware(
            owner_id=OWNER_ID,
            max_requests=5,
            window_seconds=60
        )
    )

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

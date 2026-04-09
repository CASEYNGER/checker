"""
Middleware для ограничения количества запросов к боту.

Владелец бота (OWNER_ID) не ограничивается.
Для остальных пользователей действует лимит по числу сообщений за окно времени.
"""

import time
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject


class RateLimitMiddleware(BaseMiddleware):
    """
    Ограничивает количество пользовательских запросов за фиксированное окно времени.

    :param owner_id: Telegram user ID владельца бота, для него лимит не применяется.
    :param max_requests: Максимально допустимое число запросов.
    :param window_seconds: Размер временного окна в секундах.
    """

    def __init__(
        self,
        owner_id: int,
        max_requests: int = 5,
        window_seconds: int = 60,
    ) -> None:
        self.owner_id = owner_id
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[int, deque[float]] = defaultdict(deque)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Проверяет, не превысил ли пользователь лимит запросов.

        :param handler: Следующий middleware или хендлер в цепочке.
        :param event: Входящее событие aiogram.
        :param data: Контекстные данные события.
        :return: Результат выполнения следующего обработчика или None.
        """

        if not isinstance(event, Message):
            return await handler(event, data)

        user = event.from_user
        if user is None:
            return await handler(event, data)

        if user.id == self.owner_id:
            return await handler(event, data)

        now = time.monotonic()
        user_requests = self._requests[user.id]

        while user_requests and now - user_requests[0] > self.window_seconds:
            user_requests.popleft()

        if len(user_requests) >= self.max_requests:
            await event.answer(
                f'⚠️ Слишком много запросов. '
                f'Лимит: {self.max_requests} за {self.window_seconds} сек.'
            )
            return None

        user_requests.append(now)
        return await handler(event, data)

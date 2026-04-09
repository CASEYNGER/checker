"""
Модуль инлайн-клавиатур Telegram-бота.

Содержит фабрики клавиатур для:
- стартового сообщения;
- страницы с описанием возможностей бота.

Клавиатуры используются для навигации между сообщениями через callback_data.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру для стартового сообщения бота.

    Клавиатура содержит одну кнопку:
    - "Что ты умеешь?" — открывает страницу с описанием возможностей бота через callback_data `what_can_you_do`.

    :return:
        Объект `InlineKeyboardMarkup` для отображения под стартовым сообщением.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='Что ты умеешь?',
                    callback_data='what_can_you_do'
                )
            ]
        ]
    )

def capabilities_keyboard() -> InlineKeyboardMarkup:
    """
    Создаёт инлайн-клавиатуру для страницы с возможностями бота.

    Клавиатура содержит одну кнопку:
    - "<< Назад" — возвращает пользователя к стартовому сообщению
      через callback_data `back_to_start`.

    :return:
        Объект `InlineKeyboardMarkup` для отображения под сообщением
        с описанием возможностей бота.
    """

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text='<< Назад',
                    callback_data='back_to_start'
                )
            ]
        ]
    )

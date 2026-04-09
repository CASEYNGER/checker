"""
Модуль хендлера проверки VIN.

Содержит универсальный message-handler, который принимает текстовое сообщение
пользователя, интерпретирует его как VIN-номер, запускает валидацию через
`validate_input_vin` и возвращает либо список ошибок, либо расшифрованную
информацию по VIN.

Предполагается, что данный хендлер подключается после /start-хендлеров
и обрабатывает произвольный пользовательский ввод.
"""

from aiogram import Router
from aiogram.types import Message

from core.utils.validator import validate_input_vin

router = Router()


@router.message()
async def validate_vin_handler(message: Message) -> None:
    """
    Обрабатывает входящее текстовое сообщение как VIN для проверки.

    Логика работы:
    1. Получает текст сообщения от пользователя.
    2. Удаляет лишние пробелы по краям.
    3. Если сообщение пустое, просит пользователя отправить VIN.
    4. Передаёт значение в `validate_input_vin`.
    5. Если VIN не прошёл проверку, отправляет пользователю список ошибок.
    6. Если VIN валиден, формирует подробный ответ с расшифровкой:
       - WMI, VDS, VIS;
       - статус контрольного символа;
       - страна производства;
       - код страны;
       - бренд;
       - владелец бренда;
       - завод-изготовитель;
       - модельный год.

    :param message:
        Объект входящего сообщения Telegram от пользователя.
        Ожидается, что `message.text` содержит VIN или произвольный текст.
    :return:
        Ничего не возвращает. Отправляет ответное сообщение пользователю.
    """

    vin_value = (message.text or '').strip()

    if not vin_value:
        await message.answer('Отправь мне VIN для проверки')
        return

    result = validate_input_vin(vin_value)

    if not result.is_valid:
        errors_text = '\n'.join(f'• {error}' for error in result.errors)
        await message.answer(f'❌ *VIN не прошёл проверку*:\n\n{errors_text}')
        return

    data = result.data
    text = (
        f'✅ *ИНФОРМАЦИЯ О VIN*: {data["vin"]}\n\n'
        f'*WMI*: {data["wmi"]}\n'
        f'*VDS*: {data["vds"]}\n'
        f'*VIS*: {data["vis"]}\n\n'
        f'*Контрольный символ*: {data["is_valid_control_symbol"]}\n\n'
        f'– *Страна производства*: {data["country"]}\n'
        f'– *Код страны*: {data["country_code"]}\n'
        f'– *Бренд*: {data["brand_name"]}\n'
        f'– *Владелец бренда*: {data["brand_owner"]}\n'
        f'– *Завод-изготовитель*: {data["manufacturer"]}\n'
        f'– *Модельный год*: {data["model_year"]}'
    )
    await message.answer(text)

from aiogram import Router
from aiogram.types import Message

from core.utils.validator import validate_input_vin

router = Router()


@router.message()
async def validate_vin_handler(message: Message) -> None:
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
        f'✅ *ИНФОРМАЦИЯ О VIN*\n\n'
        f'*WMI*: {data["wmi"]}\n'
        f'*VDS*: {data["vds"]}\n'
        f'*VIS*: {data["vis"]}\n\n'
        f'– *Страна производства*: {data["country"]}\n'
        f'– *Завод-изготовитель*: {data["manufacturer"]}\n'
        f'– *Модельный год*: {data["model_year"]}'
    )
    await message.answer(text)

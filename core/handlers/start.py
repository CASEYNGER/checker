from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        'Отправь мне VIN и я помогу его проверить.'
    )
"""
Модуль с глобальными настройками бота.
"""

import os

from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()

PARSE_MODE = ParseMode.MARKDOWN
OWNER_ID = int(os.getenv('OWNER_ID', 'O'))

"""
Модуль с константами и справочными данными для валидации VIN.

Содержит:
- набор разрешённых символов VIN;
- загрузку приватного WMI-справочника из JSON по пути из переменной окружения;
- загрузку таблицы соответствия кодов модельного года `YEAR_CODES`;
- таблицу "весов" буквенных символов для расчёта контрольного числа;
- кортеж весов позиций VIN;
- текстовые константы сообщений об ошибках.

Переменная окружения:
    WMI_DATA_PATH: абсолютный путь к приватному файлу `wmi.json`
    (или `wmi_flat.json`), не хранящемуся в репозитории.
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


# Загружаем переменные окружения из .env (если он есть в проекте).
# После этого WMI_DATA_PATH доступен через os.getenv / os.environ.
load_dotenv()

# Разрешенные символы VIN (без I, O, Q согласно ISO-3779).
ALLOWED_SYMBOLS: tuple[str, ...] = tuple('ABCDEFGHJKLMNPRSTUVWXYZ0123456789')

# Путь к приватному WMI-справочнику задается только через env,
# чтобы не хранить чувствительные данные / IP в репозитории.
_WMI_DATA_PATH_ENV = os.getenv('WMI_DATA_PATH')
if not _WMI_DATA_PATH_ENV:
    raise ValueError(
        'WMI_DATA_PATH не найден в окружении. '
        'Укажи абсолютный путь к приватному wmi.json'
    )

_WMI_MANUFACTURERS_PATH = Path(_WMI_DATA_PATH_ENV).expanduser().resolve()
with _WMI_MANUFACTURERS_PATH.open('r', encoding='utf-8') as wmi_file:
    # Справочник WMI
    WMI_MANUFACTURERS: dict[str, dict[str, str | None]] = json.load(wmi_file)

# Берем absolute path до core/data/year_codes.json.
_YEAR_CODES_PATH = Path(__file__).resolve().parent.parent / 'data' / 'year_codes.json'
with _YEAR_CODES_PATH.open('r', encoding='utf-8') as year_codes_file:
    # Таблица соответствия: символ модельного года -> год (int).
    YEAR_CODES: dict[str, int] = json.load(year_codes_file)

# "Вес" символов идентификационного номера для расчёта контрольного числа VIN.
# Цифры используются как есть (0..9), для букв берём значение из этой таблицы.
NUMBER_WEIGHT: dict[str, int] = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5,
    'F': 6, 'G': 7, 'H': 8, 'J': 1, 'K': 2,
    'L': 3, 'M': 4, 'N': 5, 'P': 7, 'R': 9,
    'S': 2, 'T': 3, 'U': 4, 'V': 5, 'W': 6,
    'X': 7, 'Y': 8, 'Z': 9,
}

# Веса позиций VIN (1..17) для расчёта контрольного символа (ISO-3779).
# Индекс в кортеже соответствует позиции символа (0-based).
POSITIONS = (8, 7, 6, 5, 4, 3, 2, 10, 0, 9, 8, 7, 6, 5, 4, 3, 2)

# Текстовые константы для сообщений об ошибках валидации VIN.
UNCORRECT_VALUE = 'Количество знаков VIN некорректно:'
UNCORRECT_SYMBOL = 'Найдены некорректные символы:'
NOT_ONLY_DIGITS = 'VIN не может состоять только из цифр'
NOT_ONLY_LETTERS = 'VIN не может состоять только из букв'

import json
from pathlib import Path

ALLOWED_SYMBOLS = tuple('ABCDEFGHJKLMNPRSTUVWXYZ0123456789')

# Путь формируется от текущего файла, чтобы загрузка работала из любой рабочей директории.
_WMI_MANUFACTURERS_PATH = Path(__file__).resolve().parent.parent / 'data' / 'wmi.json'
with _WMI_MANUFACTURERS_PATH.open('r', encoding='utf-8') as wmi_file:
    WMI_MANUFACTURERS = json.load(wmi_file)

# Аналогично: берем absolute path до core/data/country_codes.json.
_COUNTRY_CODES_PATH = Path(__file__).resolve().parent.parent / 'data' / 'country_codes.json'
with _COUNTRY_CODES_PATH.open('r', encoding='utf-8') as country_codes_file:
    COUNTRY_CODES = json.load(country_codes_file)

# Берем absolute path до core/data/year_codes.json.
_YEAR_CODES_PATH = Path(__file__).resolve().parent.parent / 'data' / 'year_codes.json'
with _YEAR_CODES_PATH.open('r', encoding='utf-8') as year_codes_file:
    YEAR_CODES = json.load(year_codes_file)

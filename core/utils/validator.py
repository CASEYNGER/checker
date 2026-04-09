"""Модуль, отвечающий за валидацию VIN и формирование результата для бота.

Содержит:
- dataclass VINValidationResult — единый формат результата проверки VIN;
- класс VINValidator — реализация правил ISO-3779 для VIN с 2001 г.;
- функцию validate_input_vin — удобную обёртку для использования в хендлерах.
"""

from datetime import datetime as dt
from dataclasses import dataclass, field
from typing import List

from core.utils.constants import (
    ALLOWED_SYMBOLS, YEAR_CODES, WMI_MANUFACTURERS,
    NUMBER_WEIGHT, POSITIONS, UNCORRECT_VALUE,
    UNCORRECT_SYMBOL, NOT_ONLY_DIGITS, NOT_ONLY_LETTERS
)


@dataclass
class VINValidationResult:
    """
    Результат валидации идентификационного номера (VIN) по стандарту ISO-3779.

    Атрибуты:
        is_valid: Флаг, указывающий, прошёл ли VIN проверку (True/False).
        errors: Список текстовых сообщений об ошибках (если они были).
        data: Словарь с деталями разборки VIN при успешной валидации.
    """

    is_valid: bool = False
    """Статус валидации"""

    errors: List[str] = field(default_factory=list)
    """Список ошибок валидации."""

    data: dict[str, object] = field(default_factory=dict)
    """Данные разборки VIN при успехе."""


class VINValidator:
    """
    Класс для валидации идентификационного номера (VIN) транспортных средств,
    выпущенных с 2001 года включительно, по международному стандарту ISO-3779.

    Валидация включает:
    - проверку длины и допустимых символов;
    - проверку, что VIN не состоит только из цифр или только из букв;
    - разбор VIN на части (WMI, VDS, VIS);
    - декодирование WMI (бренд, страна, производитель и т.п.);
    - определение модельного года по коду;
    - проверку контрольного символа VIN.

    Args:
        vin_value: Входной VIN, может содержать лишние пробелы и произвольный регистр.
                   В конструкторе значение нормализуется: пробелы по краям удаляются,
                   все символы приводятся к верхнему регистру.
    """

    def __init__(self, vin_value: str) -> None:
        """Инициализирует валидатор с нормализацией VIN (strip + upper)."""

        self.vin_value = vin_value.strip().upper()
        self.errors: List[str] = []

    def _add_error(self, message: str) -> None:
        """Внутренний метод для накопления ошибок."""

        self.errors.append(message)

    def _check_length(self) -> bool:
        """
        Проверяет длину VIN.

        :return: True, если длина соответствует ISO-3779, иначе False
        """

        is_valid = len(self.vin_value) == 17
        if not is_valid:
            self._add_error(f'{UNCORRECT_VALUE} {len(self.vin_value)}')

        return is_valid

    def _check_forbidden_symbols(self) -> bool:
        """
        Проверяет наличие запрещенных символов.

        :return: True, если символы соответствуют ISO-3779, иначе False
        """

        separated_vin: List[str] = list(self.vin_value)
        forbidden_found = [symbol for symbol in separated_vin if symbol not in ALLOWED_SYMBOLS]

        if forbidden_found:
            self._add_error(f'{UNCORRECT_SYMBOL} {list(forbidden_found)}')
            return False

        return True

    def _check_is_not_only_digits(self) -> bool:
        """
        Проверяет, что VIN не состоит только из цифр.

        :return: True / False
        """

        if not self.vin_value.isdigit():
            return True
        self._add_error(NOT_ONLY_DIGITS)

        return False

    def _check_is_not_only_letters(self) -> bool:
        """
        Проверяет, что VIN не состоит только из букв.

        :return: True / False
        """

        if not self.vin_value.isalpha():
            return True
        self._add_error(NOT_ONLY_LETTERS)

        return False

    def _parse_vin(self) -> dict[str, str]:
        """
        Разбирает VIN на составляющие части (WMI, VDS, VIS).

        :return: Словарь с ключами: WMI, VDS, VIS
        """

        return {
            'WMI': self.vin_value[:3],     # WMI - World Manufacturer Identifier
            'VDS': self.vin_value[3:9],    # VDS - Vehicle Descriptor Section
            'VIS': self.vin_value[9:]      # VIS - Vehicle Identification Section
        }

    def _decode_wmi(self) -> dict[str, str | None]:
        """
        Декодирует WMI.

        :return: Словарь с информацией о WMI
        """

        wmi = self._parse_vin()['WMI']
        raw = WMI_MANUFACTURERS.get(wmi)

        if raw is not None:
            return raw

        return {
            'brand_name': None,
            'country': None,
            'manufacture': None,
            'brand_owner': None,
            'country_code': None
        }

    def _parse_model_year_code(self) -> str:
        """
        Извлекает год выпуска.

        :return: Символ на 10-ой позиции
        """

        return self.vin_value[9]

    @staticmethod
    def _get_value(char) -> int:
        """
        Возвращает числовое значение символа VIN (0..9 или таблица для букв).

        :return: Числовое значение символа
        """

        value = None
        if char.isdigit():
            value = int(char)
        if char in NUMBER_WEIGHT:
            value = NUMBER_WEIGHT[char]

        return value

    def _check_control_symbol(self) -> int:
        """
        Возвращает контрольное число (sum % 11) для VIN‑номера длиной 17 символов.

        :return: контрольное число 0..9 или 10
        """

        total = 0
        for i, char in enumerate(self.vin_value):
            if i == 8:  # 9‑й символ — не участвует в расчёте
                continue
            value = self._get_value(char)
            total += value * POSITIONS[i]

        checksum = total % 11

        control_symbol = self.vin_value[8]
        if control_symbol == 'X' and checksum == 10:
            return True
        if control_symbol.isdigit() and int(control_symbol) == checksum:
            return True

        return False

    def _check_is_valid(self) -> bool:
        """
        Комплексная проверка всех базовых требований в соответствии с ISO-3779.

        :return: True / False
        """

        checks = [
            self._check_length(),
            self._check_forbidden_symbols(),
            self._check_is_not_only_digits(),
            self._check_is_not_only_letters(),
        ]

        return all(checks)

    def validate(self) -> VINValidationResult:
        """
        Основной метод валидации VIN с разбором на структурные компоненты
        и возвратом структурированного результата.

        Алгоритм работы:
        1. Сначала выполняется комплексная базовая проверка VIN через `self._check_is_valid`.
        2. Если базовая проверка провалена, сразу возвращается `VINValidationResult`.
        3. Если базовая проверка пройдена, выполняется разбор VIN на составные части (WMI, VDS, VIS).
        4. WMI декодируется через `self._decode_wmi` в словарь.
        5. Проверяется модельный год.
        6. Проверяется контрольный символ.
        7. Если в процессе возникли ошибки (`self.errors` != []), возвращаются.
        8. Если ошибок нет, формируется и возвращается `VINValidationResult(is_valid=True)`.

        :return:
            VINValidationResult с полями:
            - is_valid (bool): флаг, прошел ли VIN все заданные проверки;
            - errors (List[str]): список текстовых сообщений об ошибках;
            - data (dict[str, object]): при успешной валидации содержит:
                - vin: нормализованный VIN в верхнем регистре,
                - wmi: WMI,
                - vds: VDS,
                - vis: VIS,
                - brand_name: название бренда по WMI или None,
                - country: страна-производитель или None,
                - country_code: код страны или None,
                - manufacturer: завод-изготовитель или None,
                - brand_owner: владелец бренда или None,
                - model_year: год модели по коду модельного года или None,
                - is_valid_control_symbol: строка, отражающая результат проверки контрольного символа
        """

        if not self._check_is_valid():
            return VINValidationResult(
                is_valid=False,
                errors=self.errors.copy()
            )

        parts = self._parse_vin()
        decoded_wmi_parts: dict[str, str] = self._decode_wmi()

        # Название бренда
        brand_name: str = decoded_wmi_parts.get('brand_name') or None
        if not brand_name:
            self._add_error('Неизвестный бренд')

        # Страна-производитель
        country: str = decoded_wmi_parts.get('country') or None
        if not country:
            self._add_error('Неизвестная страна')

        # Завод-изготовитель
        manufacturer: str = decoded_wmi_parts.get('manufacture') or None
        if not manufacturer:
            self._add_error('Неизвестный завод-изготовитель')

        # Владелец бренда
        brand_owner: str = decoded_wmi_parts.get('brand_owner') or None
        if not brand_owner:
            self._add_error('Неизвестный владелец бренда')

        # Код страны
        country_code: str = decoded_wmi_parts.get('country_code') or None
        if not country_code:
            self._add_error('Неизвестный код страны')

        # Проверка кода модельного года
        model_year_code = self._parse_model_year_code()
        model_year = YEAR_CODES.get(model_year_code)
        if model_year is None:
            self._add_error('Неизвестный код модельного года')
        elif model_year > dt.now().year:
            self._add_error('Год выпуска не может быть меньше текущего')

        # Проверка контрольного символа
        check_control_symbol = self._check_control_symbol()
        if check_control_symbol:
            is_valid_control_symbol = 'Совпадает'
        else:
            is_valid_control_symbol = '⚠️ Не совпадает'

        if self.errors:
            return VINValidationResult(
                is_valid=False,
                errors=self.errors.copy()
            )

        return VINValidationResult(
            is_valid=True,
            data={
                'vin': self.vin_value,
                'wmi': parts['WMI'],
                'vds': parts['VDS'],
                'vis': parts['VIS'],
                'brand_name': brand_name,
                'country': country,
                'country_code': country_code,
                'manufacturer': manufacturer,
                'brand_owner': brand_owner,
                'model_year': model_year,
                'is_valid_control_symbol': is_valid_control_symbol
            }
        )

def validate_input_vin(vin_value: str) -> VINValidationResult:
    """
    Функция–обертка для удобной проверки VIN.

    Используется в хендлерах бота и других частях приложения, чтобы
    не создавать экземпляр VINValidator вручную.

    :param vin_value: VIN для валидации
    :return: Объект VINValidationResult с результатами валидации
    """

    return VINValidator(vin_value).validate()

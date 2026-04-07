from dataclasses import dataclass, field
from typing import List

from core.utils.constants import ALLOWED_SYMBOLS, YEAR_CODES, COUNTRY_CODES, WMI_MANUFACTURERS


@dataclass
class VINValidationResult:
    """Результат валидации идентификационного номера (VIN) по стандарту ISO-3779."""

    is_valid: bool = False
    """Статус валидации"""

    errors: List[str] = field(default_factory=list)
    """Список ошибок валидации."""

    data: dict[str, object] = field(default_factory=dict)
    """Данные разборки VIN при успехе."""


class VINValidator:
    """
    Класс, предназначенный для валидации входящего от пользовательского значения
    идентификационного номера (VIN) транспортных средств, выпущенных с 2001 года включительно,
    разработанный в соответствии с требованиями международного стандарта ISO-3779.

    Args:
        vin_value (str): автоматически нормализующийся VIN (идентификационный номер)
    """

    def __init__(self, vin_value: str) -> None:
        """Инициализирует валидатор с нормализацией VIN (удаляет пробелы, делает uppercase)."""

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
            self._add_error(f'Количество знаков VIN некорректно ({len(self.vin_value)}).')
        return is_valid

    def _check_forbidden_symbols(self) -> bool:
        """
        Проверяет наличие запрещенных символов.

        :return: True, если символы соответствуют ISO-3779, иначе False
        """

        separated_vin: List[str] = list(self.vin_value)
        forbidden_found = [symbol for symbol in separated_vin if symbol not in ALLOWED_SYMBOLS]

        if forbidden_found:
            self._add_error(f'Найдены некорректные символы: {list(forbidden_found)}.')
            return False

        return True

    def _check_is_not_only_digits(self) -> bool:
        """
        Проверяет, что VIN не состоит только из цифр.

        :return: True / False
        """

        if not self.vin_value.isdigit():
            return True
        self._add_error('VIN не может состоять только из цифр.')
        return False

    def _check_is_not_only_letters(self) -> bool:
        """
        Проверяет, что VIN не состоит только из букв.

        :return: True / False
        """

        if not self.vin_value.isalpha():
            return True
        self._add_error('VIN не может состоять только из букв.')
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

    def _decode_wmi(self) -> str | None:
        """
        Декодирует из кода WMI название завода-изготовитель.

        :return: Название производителя по WMI или сообщение о том,
        что производитель не определён
        """

        wmi = self._parse_vin()['WMI']
        manufacturer = WMI_MANUFACTURERS.get(wmi)

        if manufacturer:
            return manufacturer

        return f'Производитель WMI={wmi} не определен.'

    def _parse_country_code(self) -> str:
        """
        Извлекает код страны.

        :return: Символ на 1-ой позиции
        """

        return self.vin_value[0]

    def _parse_model_year_code(self) -> str:
        """
        Извлекает год выпуска.

        :return: Символ на 10-ой позиции
        """

        return self.vin_value[9]

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
        Основной метод валидации VIN с разбором и выводом результата.

        :return: True, если VIN соответствует ISO-3779, иначе False
        """

        if not self._check_is_valid():
            return VINValidationResult(
                is_valid=False,
                errors=self.errors.copy()
            )

        parts = self._parse_vin()
        manufacturer = self._decode_wmi()

        # Проверка страны
        country_code = self._parse_country_code()
        country = COUNTRY_CODES.get(country_code)
        if country is None:
            self._add_error('Неизвестная страна.')

        # Проверка кода
        model_year_code = self._parse_model_year_code()
        model_year = YEAR_CODES.get(model_year_code)
        if model_year is None:
            self._add_error('Неизвестный код модельного года.')

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
                'country': country,
                'manufacturer': manufacturer,
                'model_year': model_year,
            }
        )

def validate_input_vin(vin_value: str) -> VINValidationResult:
    """
    Функция–обертка для удобной проверки VIN.

    :param vin_value: VIN для валидации
    :return: Результат валидации
    """
    return VINValidator(vin_value).validate()

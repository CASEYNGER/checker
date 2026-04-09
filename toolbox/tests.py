"""
Тесты базовой проверки длины VIN в валидаторе.
"""

from core.utils.validator import validate_input_vin, VINValidator


def test_wrong_vin_short():
    """
    VIN короче 17 символов должен быть невалидным и
    возвращать ошибку о некорректном количестве знаков.
    """

    result = validate_input_vin('vin123')

    assert result.is_valid is False
    assert any(
        'Количество знаков VIN некорректно' in e
        for e in result.errors
    )


def test_wrong_vin_long():
    """
    VIN длиннее 17 символов должен быть невалидным и
    возвращать ошибку о некорректном количестве знаков.
    """

    result = validate_input_vin('vin12345678901234567890')

    assert result.is_valid is False
    assert any(
        'Количество знаков VIN некорректно' in e
        for e in result.errors
    )

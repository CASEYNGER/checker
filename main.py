from core.utils.validator import validate_input_vin


if __name__ == "__main__":
    while True:

        get_vin = input('Введите VIN (или "exit" для выхода): ')

        if not get_vin or get_vin.lower() == 'exit':
            print('Завершение программы. До свидания!')
            break

        result = validate_input_vin(get_vin)
        print(f'Результат проверки: {result}')

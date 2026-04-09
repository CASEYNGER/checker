# VIN Decoder Bot v1.0.3

Telegram-бот и CLI-инструмент для проверки и расшифровки VIN (ISO-3779).

## Возможности

- команда `/start` с inline-навигацией по подсказкам;
- валидация базовых правил VIN:
  - длина 17 символов,
  - допустимый алфавит (без `I`, `O`, `Q`),
  - VIN не только из цифр и не только из букв;
- разбор VIN на `WMI`, `VDS`, `VIS`;
- декодирование `WMI` (бренд, владелец бренда, завод, страна, код страны);
- определение модельного года по 10-му символу;
- проверка контрольного символа VIN.

## Дисклеймер

Результат декодирования справочный. Производители могут использовать собственные внутренние правила маркировки, поэтому для критичных задач проверяйте данные по официальным источникам.

## Структура проекта

```text
checker/
├── bot.py
├── main.py
├── requirements.txt
├── .env.example
├── toolbox/
│   └── tests.py
└── core/
    ├── handlers/
    │   ├── faq.py
    │   ├── start.py
    │   └── vin.py
    ├── middlewares/
    │   └── rate_limit.py
    ├── keyboards/
    │   └── inline_keyboards.py
    ├── logging/
    │   └── logger.py
    ├── data/
    │   ├── year_codes.json
    │   ├── country_codes.json
    │   ├── <your_wmi>.json
    └── utils/
        ├── constants.py
        ├── validator.py
        └── global_configs.py
```

## Переменные окружения

```env
BOT_TOKEN=your_telegram_bot_token_here
WMI_DATA_PATH=/absolute/path/to/private/wmi.json
```

- `BOT_TOKEN` — токен Telegram-бота;
- `WMI_DATA_PATH` — обязательный абсолютный путь к приватному WMI-справочнику (не хранится в репозитории).

## Запуск

```bash
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

Локальная проверка без Telegram:

```bash
python main.py
```

Запуск тестов:

```bash
pytest toolbox/tests.py -q
```

## Как работает валидация

`validate_input_vin()` вызывает `VINValidator.validate()`:
1. базовые проверки VIN;
2. декодирование `WMI` по приватному JSON из `WMI_DATA_PATH`;
3. определение модельного года из `core/data/year_codes.json`;
4. расчет и проверка контрольного символа.

На выходе возвращается `VINValidationResult`:
- `is_valid: bool`
- `errors: list[str]`
- `data: dict` (при успехе: `vin`, `wmi`, `vds`, `vis`, `brand_name`, `brand_owner`, `manufacturer`, `country`, `country_code`, `model_year`, `is_valid_control_symbol`)

## Middlewares

- `core/middlewares/rate_limit.py` содержит `RateLimitMiddleware`;
- middleware ограничивает частоту сообщений по пользователю (`max_requests` за `window_seconds`);
- для `owner_id` лимит не применяется;
- при превышении лимита пользователь получает предупреждение.

## Пример ответа бота

Успех:

```text
✅ ИНФОРМАЦИЯ О VIN: 1HGCM8263TA004352
WMI: 1HG
...
Контрольный символ: Совпадает
```

Ошибка:

```text
❌ VIN не прошёл проверку:
• Количество знаков VIN некорректно: 16
• Найдены некорректные символы: ['I']
```

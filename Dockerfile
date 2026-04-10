# Указываем базовый образ – минимальная Python 3.12
FROM python:3.12-slim

# Задаем название рабочей директории для дальнейших инструкций
WORKDIR /app

# Копируем только файл зависимостей в /app. Это ключевой
# трюк для кэша, если файл зависимостей не изменился – pip install
# НЕ выполнится повторно
COPY requirements.txt .
# Устанавливаем пакеты во время сборки, создает слой site-packages
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в /app
COPY . .

# Задаем переменную в окружение образа, чтобы код нашел файл внутри контейнера
#ENV WMI_DATA_PATH=/app/core/data/wmi_flat.json

# Команда для запуска бота
CMD ["python", "bot.py"]

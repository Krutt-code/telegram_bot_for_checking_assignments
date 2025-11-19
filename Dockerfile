# Используем официальный образ Python
FROM python:3.13-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /usr/src/app

# Устанавливаем зависимости
COPY poetry.lock .
RUN pip install --no-cache-dir poetry
RUN poetry install --no-root

COPY ./src ./src
COPY ./main.py .

# Открываем порт
EXPOSE 8000

# Указываем команду запуска бота
CMD ["python", "-m", "main"]

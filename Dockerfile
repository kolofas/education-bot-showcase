# Используем официальный Python-образ
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Системные зависимости для psycopg2, alembic и т.д.
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Указываем рабочую директорию
ENV PYTHONPATH=/app

# Вибираємо базовий образ
FROM python:3.10-slim

# Оновлення і встановлення gcc для пакетів з C розширеннями
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо requirements
COPY requirements.txt .

# Актуалізація pip і установка залежностей
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

# Виставляємо порт для Render
ENV PORT=10000

# Команда запуску
CMD ["python", "app.py"]
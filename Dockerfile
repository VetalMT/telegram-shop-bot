# Базовий образ з Python 3.10
FROM python:3.10-slim

# Змінні оточення (за замовчуванням)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (якщо знадобляться для sqlite/aio по збірці)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо вимоги і ставимо
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проєкт
COPY . .

# Виставляємо порт
ENV PORT=10000

# Команда запуску
CMD ["python", "app.py"]

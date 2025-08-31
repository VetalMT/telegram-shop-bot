# Використовуємо офіційний Python образ
FROM python:3.11-slim

# Встановлюємо залежності для psycopg2
RUN apt-get update && apt-get install -y build-essential libpq-dev

# Створюємо робочу директорію
WORKDIR /app

# Копіюємо залежності
COPY requirements.txt .

# Встановлюємо пакети
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

# Запуск бота
CMD ["python", "app.py"]

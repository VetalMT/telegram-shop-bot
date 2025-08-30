# Використовуємо легкий образ Python
FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Встановлюємо системні залежності (щоб asyncpg, psycopg2 і reportlab зібрались)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements.txt
COPY requirements.txt .

# Встановлюємо Python-залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь код у контейнер
COPY . .

# Відкриваємо порт (якщо треба для webhook)
EXPOSE 8080

# Запуск бота
CMD ["python", "app.py"]

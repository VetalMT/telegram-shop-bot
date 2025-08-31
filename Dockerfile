# Використовуємо легкий офіційний образ Python
FROM python:3.11-slim

# Встановлюємо залежності для роботи з PostgreSQL та системні пакети
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Встановлюємо залежності Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо увесь проект
COPY . .

# Вказуємо змінну оточення
ENV PYTHONUNBUFFERED=1

# Запускаємо бота
CMD ["python", "app.py"]

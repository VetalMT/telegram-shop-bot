# Базовий образ
FROM python:3.11-slim

# Встановлюємо залежності системи
RUN apt-get update && apt-get install -y build-essential

# Робоча директорія
WORKDIR /app

# Копіюємо файли
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Запуск
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]

# Базовий образ Python 3.10
FROM python:3.10-slim

# Робоча директорія
WORKDIR /app

# Копіюємо файли проєкту
COPY . .

# Встановлюємо залежності
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Порт, на якому працює бот (для Render)
EXPOSE 10000

# Команда старту
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]

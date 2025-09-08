# Базовий імідж
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Системні залежності (за потреби розкоментуй sqlite3-cli)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Робоча директорія
WORKDIR /app

# Встановлення Python-залежностей
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Копіюємо код
COPY . .

# Порт (Render зазвичай підставляє PORT)
EXPOSE 10000

# Запуск
CMD ["python", "app.py"]

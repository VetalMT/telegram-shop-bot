FROM python:3.10-slim

# Системні залежності
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копіюємо requirements
COPY requirements.txt .

# Актуалізація pip і установка залежностей
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

# Порт для Render
ENV PORT=10000

# Команда запуску
CMD ["python", "app.py"]
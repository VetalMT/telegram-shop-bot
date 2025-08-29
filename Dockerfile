FROM python:3.10-slim

# Оновлення та gcc
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копіюємо залежності
COPY requirements.txt .

# Оновлюємо pip та встановлюємо залежності
RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект
COPY . .

CMD ["python", "app.py"]
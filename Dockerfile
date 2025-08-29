FROM python:3.10-slim

WORKDIR /app

# Системні залежності для pdfkit (wkhtmltopdf)
RUN apt-get update && apt-get install -y gcc wkhtmltopdf && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]

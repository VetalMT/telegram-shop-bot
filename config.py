import os

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Port для Render
PORT = int(os.getenv("PORT", 8000))

# URL зовнішнього вебхука Render
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

# PostgreSQL
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Admin IDs
ADMINS = [123456789]  # <-- постав свій Telegram ID
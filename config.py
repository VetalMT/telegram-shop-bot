import os

TOKEN = os.getenv("BOT_TOKEN")  # токен твого бота з Render env vars
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # свій Telegram ID сюди

DB_PATH = "shop.db"

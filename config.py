import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "469040941"))  # змінити в Render env
DB_PATH = os.getenv("DB_PATH", "shop.db")

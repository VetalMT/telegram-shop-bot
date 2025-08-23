import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # додай свій у Render env
DB_PATH = "shop.db"

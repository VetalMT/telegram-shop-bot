import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "469040941"))
DATABASE_URL = os.getenv("DATABASE_URL")  # <--- беремо з Render

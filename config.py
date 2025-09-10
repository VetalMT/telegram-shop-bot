import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # налаштуй в Render/Env
DB_PATH = os.getenv("DB_PATH", "shop.db")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # повинен бути типу https://example.com

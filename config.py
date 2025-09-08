import os

# Обов'язково в env:
# BOT_TOKEN, ADMIN_ID, RENDER_EXTERNAL_URL, PORT (опційно)
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

# Шлях до SQLite (у контейнері пишемо у робочу директорію)
DB_PATH = os.getenv("DB_PATH", "shop.db")

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "shop.db")
# WEBHOOK_HOST можна задати як WEBHOOK_HOST або Render дає RENDER_EXTERNAL_URL
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST") or os.getenv("RENDER_EXTERNAL_URL")

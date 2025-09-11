import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # постав свій ADMIN_ID у Render env
DB_PATH = os.getenv("DB_PATH", "shop.db")
# WEBHOOK_HOST: від Render це часто RENDER_EXTERNAL_URL, або задай свій WEBHOOK_HOST (https://...)
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST") or os.getenv("RENDER_EXTERNAL_URL")

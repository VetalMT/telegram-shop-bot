import os

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN")

# 🛡️ ID адміністратора
ADMIN_ID = os.getenv("ADMIN_ID")
if not ADMIN_ID:
    raise ValueError("❌ Не вказано ADMIN_ID")
ADMIN_ID = int(ADMIN_ID)

# 🌍 Webhook URL (Render виставляє RENDER_EXTERNAL_URL)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
if not RENDER_EXTERNAL_URL:
    raise ValueError("❌ Не вказано RENDER_EXTERNAL_URL")
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

# 📦 PostgreSQL налаштування
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT", 5432))

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise ValueError("❌ Не всі змінні для PostgreSQL вказані (DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)")

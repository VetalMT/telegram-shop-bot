import os

# Токен беремо з Environment Variables (Render → Settings → Environment)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено! Додай його у Render Environment Variables.")

# Формуємо вебхук URL
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", f"https://{os.getenv('RENDER_SERVICE_NAME')}.onrender.com")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Для запуску вебсервера на Render
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))

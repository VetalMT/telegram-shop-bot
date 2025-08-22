import os

# Фолбеки для локального запуску. На Render вистачить ENV.
BOT_TOKEN = os.getenv("BOT_TOKEN", "PASTE_YOUR_TOKEN_HERE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))  # твій Telegram ID
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # напр.: https://your-service.onrender.com/webhook

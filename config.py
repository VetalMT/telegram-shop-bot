import os

TOKEN = os.getenv("BOT_TOKEN")  # <-- твій токен з Render Env Vars

WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", f"https://{os.getenv('RENDER_SERVICE_NAME')}.onrender.com")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"  # для Render
WEBAPP_PORT = int(os.getenv("PORT", 10000))

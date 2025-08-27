import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен твого бота
DATABASE_URL = os.getenv("DATABASE_URL")  # URL до PostgreSQL Render
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")  # https://your-app.onrender.com
PORT = int(os.getenv("PORT", 10000))

ADMIN_ID = int(os.getenv("ADMIN_ID", 123456789))  # твій Telegram ID
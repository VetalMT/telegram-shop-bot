import os

from dotenv import load_dotenv

# Локально дозволяє читати .env, на Render просто ігнорується (бо ENV вже заданий)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# Render виставляє це значення автоматично
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL") or ""
DATABASE_URL = os.getenv("DATABASE_URL") or ""

# Порт, на якому слухає aiohttp (на Render повинен збігатися з $PORT)
PORT = int(os.getenv("PORT", "10000"))

if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")
if not ADMIN_ID:
    raise ValueError("❌ Не вказано ADMIN_ID в змінних оточення!")
if not RENDER_EXTERNAL_URL:
    raise ValueError("❌ Не вказано RENDER_EXTERNAL_URL в змінних оточення!")
if not DATABASE_URL:
    raise ValueError("❌ Не вказано DATABASE_URL в змінних оточення!")
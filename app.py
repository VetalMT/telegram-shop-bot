import logging
import os
from aiohttp import web
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.filters import CommandStart
from aiogram.types import Message

# -------------------------------------------------
# Налаштування логів
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# ENV змінні (Render -> Environment)
# -------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}/webhook"

# -------------------------------------------------
# Бот і диспетчер
# -------------------------------------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -------------------------------------------------
# Підключення до бази
# -------------------------------------------------
async def connect_db():
    try:
        conn = await asyncpg.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
        )
        await conn.close()
        logger.info("✅ Database connected")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")

# -------------------------------------------------
# Хендлери
# -------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("👋 Привіт! Бот працює на Render з вебхуком ✅")

@dp.message()
async def echo(message: types.Message):
    await message.answer(f"Ти написав: {message.text}")

# -------------------------------------------------
# Webhook & Aiohttp
# -------------------------------------------------
async def on_startup(app: web.Application):
    await connect_db()
    try:
        await bot.set_webhook(WEBHOOK_URL)
        logger.info(f"✅ Webhook set to {WEBHOOK_URL}")
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")

async def on_shutdown(app: web.Application):
    try:
        await bot.delete_webhook()
        logger.info("✅ Webhook deleted")
    except Exception as e:
        logger.error(f"❌ Failed to delete webhook: {e}")

def main():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
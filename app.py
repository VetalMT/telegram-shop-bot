import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, Update
from aiogram.fsm.storage.memory import MemoryStorage
import asyncpg

# ------------------------
# Налаштування логів
# ------------------------
logging.basicConfig(level=logging.INFO)

# ------------------------
# ENV змінні (Render → Environment)
# ------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

PORT = int(os.getenv("PORT", 10000))

# ------------------------
# Ініціалізація
# ------------------------
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ------------------------
# Підключення до PostgreSQL
# ------------------------
async def create_db_pool():
    return await asyncpg.create_pool(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST
    )

db_pool = None

# ------------------------
# Хендлери
# ------------------------
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer("👋 Привіт! Бот успішно працює на Aiogram 3 + PostgreSQL 🚀")

@dp.message()
async def echo_handler(message: Message):
    await message.answer(f"Ти написав: {message.text}")

# ------------------------
# Вебхук
# ------------------------
async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)  # ✅ Aiogram 3 синтаксис
    except Exception as e:
        logging.error(f"Webhook error: {e}")
    return web.Response()

# ------------------------
# On Startup / Shutdown
# ------------------------
async def on_startup(app: web.Application):
    global db_pool
    db_pool = await create_db_pool()
    logging.info("✅ Database connected")

    # Встановлюємо вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()
    if db_pool:
        await db_pool.close()
    logging.info("🛑 Bot stopped")

# ------------------------
# Запуск aiohttp
# ------------------------
def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, port=PORT)

if __name__ == "__main__":
    main()
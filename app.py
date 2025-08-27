import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from db import init_db  # наш новий asyncpg db.py
from handlers import router as main_router

# Логування
logging.basicConfig(level=logging.INFO)

# Токен бота і вебхук
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # твій домен на Render
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(main_router)

# ---------- STARTUP / SHUTDOWN ----------
async def on_startup(app: web.Application):
    await init_db()  # створюємо пул + таблиці
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook встановлено: %s", WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    logging.info("Webhook видалено")

# ---------- MAIN ----------
def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Webhook handler
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
import logging
import os
import asyncio

from aiogram import Bot, Dispatcher
from aiohttp import web

# наші модулі
from handlers_admin import admin_router
from handlers_user import user_router
from db import init_db   # ✅ тепер беремо ініціалізацію бази

logging.basicConfig(level=logging.INFO)

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не задано у змінних середовища!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# реєстрація роутерів
dp.include_router(admin_router)
dp.include_router(user_router)

# ==================
# Webhook settings
# ==================
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")  # Render URL
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def on_startup(app):
    # ✅ ініціалізація бази даних
    await init_db()

    # встановлюємо webhook
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.session.close()

# aiohttp сервер
async def handle(request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()
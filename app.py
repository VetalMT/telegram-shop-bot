import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiohttp import web

from handlers_admin import admin_router
from handlers_user import user_router
from handlers_shop import shop_router
from db import init_db

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")

# Формуємо URL вебхука з ENV (WEBHOOK_URL має пріоритет)
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") or (RENDER_URL.rstrip("/") + "/webhook" if RENDER_URL else None)
if not WEBHOOK_URL:
    raise ValueError("❌ Не знайдено WEBHOOK_URL або RENDER_EXTERNAL_URL!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Підключаємо всі роутери
dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(shop_router)

# ---------- HTTP маршрути ----------
async def health(request: web.Request):
    return web.Response(text="ok")

async def handle_webhook(request: web.Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

# ---------- Життєвий цикл ----------
async def on_startup(app: web.Application):
    await init_db()
    await bot.set_webhook(
        WEBHOOK_URL,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("⚠️ Бот зупиняється...")
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_post("/webhook", handle_webhook)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", "10000")))

if __name__ == "__main__":
    main()

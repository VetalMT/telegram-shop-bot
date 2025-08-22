import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiohttp import web

from handlers_admin import setup_admin_handlers
from handlers_shop import setup_shop_handlers
from handlers_user import user_router
from db import init_db

# 🔧 Логування
logging.basicConfig(level=logging.INFO)

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")

# 🌍 URL твого додатку (Render надає https://...)
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}/webhook"

# ================== Налаштування бота ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(user_router)  # підключаємо користувацькі хендлери

# ================== Хендлери ==================
setup_admin_handlers(dp)
setup_shop_handlers(dp)

# ================== Webhook ==================
async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def on_startup(app: web.Application):
    await init_db()  # Ініціалізація БД
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("⚠️ Бот зупиняється...")
    await bot.session.close()

# ================== Запуск ==================
def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

if __name__ == "__main__":
    main()

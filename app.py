import logging
import os
import asyncio

from aiogram import Bot, Dispatcher
from aiohttp import web

# наші модулі
from handlers_admin import admin_router
from handlers_user import user_router
from db import init_db

logging.basicConfig(level=logging.INFO)

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Встановіть BOT_TOKEN у Render Environment Variables")

# створюємо бота і диспетчер
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# підключаємо хендлери
dp.include_router(admin_router)
dp.include_router(user_router)


async def on_startup():
    logging.info("🚀 Стартуємо бот")
    init_db()  # створюємо таблиці, якщо немає


# aiohttp webhook сервер
async def handle(request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()


async def start():
    await on_startup()

    app = web.Application()
    app.router.add_post(f"/webhook/{BOT_TOKEN}", handle)

    # отримуємо RENDER зовнішній URL
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if not render_url:
        raise ValueError("❌ Встановіть RENDER_EXTERNAL_URL у Render Environment Variables")

    # встановлюємо webhook
    await bot.set_webhook(f"{render_url}/webhook/{BOT_TOKEN}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
    await site.start()

    logging.info("✅ Webhook сервер запущено")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(start())
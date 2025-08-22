import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message, Update
from aiohttp import web
from handlers_admin import admin_router
from handlers_shop import shop_router
from db import init_db

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# підключаємо роутери
dp.include_router(admin_router)
dp.include_router(shop_router)

@dp.message()
async def cmd_start(message: Message):
    await message.answer("👋 Привіт! Бот працює через Webhook на Render.")

# --- Обробка вебхука ---
async def handle_webhook(request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

async def on_startup(app):
    await init_db()  # створюємо таблицю, якщо немає
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()

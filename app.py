import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart

from config import BOT_TOKEN, WEBHOOK_URL
from keyboards import shop_kb
from db import init_db
from handlers_admin import admin_router
from handlers_shop import shop_router

# --- BOT/DP ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# підключаємо всі хендлери
dp.include_router(admin_router)
dp.include_router(shop_router)

# базовий /start (для випадку, якщо роутер не перехопив)
@dp.message(CommandStart())
async def base_start(msg: Message):
    await msg.answer("👋 Привіт! Це магазин у Telegram.", reply_markup=shop_kb)

# --- Webhook handler ---
async def handle_webhook(request: web.Request) -> web.Response:
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

# --- Startup/Shutdown ---
async def on_startup(app: web.Application):
    await init_db()
    # встановлюємо вебхук (тільки якщо URL вказаний)
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()

import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from config import BOT_TOKEN, ADMIN_ID, WEBHOOK_URL
from db import init_db
from handlers_admin import admin_router
from handlers_user import user_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(user_router)

# Клавіатури
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("📦 Каталог"), KeyboardButton("🛒 Корзина")]],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton("➕ Додати товар")],
              [KeyboardButton("❌ Видалити товар")],
              [KeyboardButton("📋 Переглянути товари")]],
    resize_keyboard=True
)

# Старт
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Вітаю, адміністратор!", reply_markup=admin_kb)
    else:
        await message.answer("Вітаю у магазині!", reply_markup=main_kb)

# Webhook
async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def on_startup(app: web.Application):
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("⚠️ Бот зупиняється...")
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    async def health(request: web.Request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

if __name__ == "__main__":
    main()

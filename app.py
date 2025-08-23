import logging
import os
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiohttp import web

# наші модулі
from handlers_admin import admin_router
from handlers_user import user_router
from db import init_db

logging.basicConfig(level=logging.INFO)

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")

# 🛡️ ID адміністратора
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
if not ADMIN_ID:
    raise ValueError("❌ Не вказано ADMIN_ID в змінних оточення!")

# 🌍 Webhook URL (Render виставляє RENDER_EXTERNAL_URL)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
if not RENDER_EXTERNAL_URL:
    raise ValueError("❌ Не вказано RENDER_EXTERNAL_URL в змінних оточення!")

WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

# ================== Налаштування бота ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== Клавіатури ==================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Каталог"), KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📋 Переглянути товари")]
    ],
    resize_keyboard=True
)

# ================== Роутери ==================
dp.include_router(admin_router)
dp.include_router(user_router)

# ================== Адмін / старт ==================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Вітаю, адміністратор!", reply_markup=admin_kb)
    else:
        await message.answer("Вітаю у магазині!", reply_markup=main_kb)

# ================== Webhook ==================
async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def on_startup(app: web.Application):
    # 1) Ініціалізувати БД
    await init_db()
    # 2) Прописати вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("⚠️ Бот зупиняється...")
    await bot.session.close()

# ================== Запуск ==================
def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    # опційно простий healthcheck на /
    async def health(request: web.Request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

if __name__ == "__main__":
    main()

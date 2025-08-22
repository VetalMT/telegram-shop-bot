import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web

from config import BOT_TOKEN, ADMIN_ID
from keyboards import shop_kb
from handlers_admin import admin_router

TOKEN = BOT_TOKEN
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # наприклад: https://твій_сайт.onrender.com/webhook

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_router(admin_router)

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привіт! Бот магазину готовий до роботи.", reply_markup=shop_kb)

# --- Обробка вебхука ---
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

# --- Старт сервера ---
async def on_startup(app):
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

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.callback_data import CallbackData
from aiogram.types.webhook import WebhookRequest, WebhookResponse
from aiogram.types.webhook import Webhook
from aiogram.fsm.storage.memory import MemoryStorage

import asyncpg
import os

# --- Логування ---
logging.basicConfig(level=logging.INFO)

# --- Токен бота і Render URL ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 10000))

# --- Підключення до PostgreSQL ---
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

async def create_pool():
    return await asyncpg.create_pool(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# --- Ініціалізація бота ---
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
db_pool = None

# --- Клавіатура ---
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📦 Каталог"), KeyboardButton("🛒 Корзина")],
    ],
    resize_keyboard=True
)

# --- Обробник старту ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Це твій магазин-бот.", reply_markup=keyboard)

# --- Обробник каталог ---
@dp.message(lambda m: m.text == "📦 Каталог")
async def show_catalog(message: types.Message):
    await message.answer("Тут буде каталог товарів.")

# --- Обробник корзини ---
@dp.message(lambda m: m.text == "🛒 Корзина")
async def show_cart(message: types.Message):
    await message.answer("Тут буде твоя корзина.")

# --- Функція для запуску webhook на Render ---
async def on_startup():
    global db_pool
    db_pool = await create_pool()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown():
    await bot.delete_webhook()
    if db_pool:
        await db_pool.close()
    await bot.session.close()

# --- Webhook endpoint ---
from aiohttp import web

async def handle(request: web.Request):
    body = await request.json()
    update = types.Update(**body)
    await dp.update.dispatch(update)
    return web.Response(text="OK")

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    web.run_app(app, host="0.0.0.0", port=PORT)

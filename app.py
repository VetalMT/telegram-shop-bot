import os
import asyncio
from aiogram import Bot, types
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Dispatcher
import aiosqlite
from dotenv import load_dotenv
from aiohttp import web

# Завантажуємо змінні середовища
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- CallbackData для кнопок ---
class BuyCallback(CallbackData, prefix="buy"):
    product_id: int

# --- Ініціалізація бази даних ---
DB_PATH = "shop.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL
            )
        """)
        await db.commit()

# --- Декілька прикладів товарів ---
PRODUCTS = [
    {"id": 1, "name": "Товар 1", "price": 100.0},
    {"id": 2, "name": "Товар 2", "price": 250.0},
    {"id": 3, "name": "Товар 3", "price": 500.0},
]

async def get_product_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    for p in PRODUCTS:
        keyboard.add(
            InlineKeyboardButton(
                text=f"Купити {p['name']} ({p['price']}₴)",
                callback_data=BuyCallback(product_id=p['id']).pack()
            )
        )
    return keyboard

# --- Обробник команд ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Ласкаво просимо до магазину! Ось наші товари:",
        reply_markup=await get_product_keyboard()
    )

# --- Обробник кнопок ---
@dp.callback_query(BuyCallback.filter())
async def buy_product(query: types.CallbackQuery, callback_data: BuyCallback):
    product = next((p for p in PRODUCTS if p['id'] == callback_data.product_id), None)
    if product:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO orders (user_id, product_id) VALUES (?, ?)",
                (query.from_user.id, product['id'])
            )
            await db.commit()
        await query.message.answer(f"Ви купили {product['name']} за {product['price']}₴ ✅")
        if ADMIN_ID:
            await bot.send_message(ADMIN_ID, f"Нове замовлення: {query.from_user.id} купив {product['name']}")
    await query.answer()

# --- Вебхук для Render ---
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.update_router.dispatch(update)
    return web.Response(text="OK")

async def on_startup(app):
    await init_db()
    # Встановлюємо вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook встановлено ✅")

# --- Запуск aiohttp сервера ---
app = web.Application()
app.router.add_post("/webhook", handle_webhook)
app.on_startup.append(on_startup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
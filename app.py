import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncpg
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

# --- FSM States ---
class ProductStates(StatesGroup):
    waiting_name = State()
    waiting_price = State()

# --- DB Pool ---
db_pool: asyncpg.pool.Pool = None

async def get_db_pool():
    global db_pool
    if not db_pool:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
    return db_pool

# --- Keyboards ---
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🛒 Створити продукт", callback_data="new_product"))
    kb.add(InlineKeyboardButton("📦 Мої продукти", callback_data="list_products"))
    return kb

# --- Handlers ---
@dp.message()
async def start_handler(message: types.Message):
    await message.answer("Привіт! Це твій магазин.", reply_markup=main_menu())

@dp.callback_query()
async def callback_handler(query: types.CallbackQuery, state: FSMContext):
    if query.data == "new_product":
        await query.message.answer("Введи назву продукту:")
        await state.set_state(ProductStates.waiting_name)
    elif query.data == "list_products":
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            products = await conn.fetch("SELECT name, price FROM products ORDER BY id DESC LIMIT 10")
        text = "\n".join([f"{p['name']} — {p['price']}₴" for p in products]) or "Продуктів немає"
        await query.message.answer(text)

@dp.message(ProductStates.waiting_name)
async def product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введи ціну продукту:")
    await state.set_state(ProductStates.waiting_price)

@dp.message(ProductStates.waiting_price)
async def product_price(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Введи число для ціни.")
        return
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO products(name, price) VALUES($1, $2)", name, price)
    await message.answer(f"Продукт {name} додано за {price}₴", reply_markup=main_menu())
    await state.clear()

# --- FastAPI Webhook ---
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(update)
    return JSONResponse(content={"ok": True})

# --- Startup/Shutdown ---
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    await get_db_pool()

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    if db_pool:
        await db_pool.close()

# --- Run via Uvicorn ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import asyncpg
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад: https://shop-x54i.onrender.com
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection string

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
db_pool = None

# --- FSM стани ---
from aiogram.fsm.state import StatesGroup, State

class Form(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_confirmation = State()

# --- FastAPI lifespan ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    # Startup
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}")
    yield
    # Shutdown
    await bot.delete_webhook()
    if db_pool:
        await db_pool.close()

app = FastAPI(lifespan=lifespan)

# --- Telegram keyboard ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎫 Створити квиток")],
        [KeyboardButton(text="ℹ Інформація")]
    ],
    resize_keyboard=True
)

# --- Telegram handlers ---
@dp.message(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Привіт! Я бот для створення PDF-квитків.", reply_markup=main_keyboard)

@dp.message(lambda message: message.text == "🎫 Створити квиток")
async def create_ticket(message: types.Message, state: FSMContext):
    await message.answer("Введіть ім'я пасажира:")
    await state.set_state(Form.waiting_for_name)

@dp.message(Form.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введіть адресу:")
    await state.set_state(Form.waiting_for_address)

@dp.message(Form.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    await message.answer(f"Підтвердіть дані:\nІм'я: {data['name']}\nАдреса: {data['address']}",
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[[KeyboardButton("✅ Підтвердити")]],
                             resize_keyboard=True
                         ))
    await state.set_state(Form.waiting_for_confirmation)

@dp.message(Form.waiting_for_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text == "✅ Підтвердити":
        data = await state.get_data()
        # Тут вставити генерацію PDF та збереження у базу
        await message.answer(f"Квиток створено для {data['name']}!", reply_markup=main_keyboard)
    await state.clear()

@dp.message(lambda message: message.text == "ℹ Інформація")
async def info(message: types.Message):
    await message.answer("Це тестовий бот для створення PDF-квитків через Telegram.")

# --- Webhook endpoint для Render ---
@app.post(f"/webhook/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(update)
    return JSONResponse(content={"ok": True})

# --- FastAPI корінь (можна для перевірки) ---
@app.get("/")
async def root():
    return {"status": "bot is running"}

# --- Запуск uvicorn тільки локально ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

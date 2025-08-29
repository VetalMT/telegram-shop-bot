# app.py
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

app = FastAPI()


# --- Keyboards ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог"), KeyboardButton(text="Кошик")]
    ],
    resize_keyboard=True
)


# --- Handlers ---
@dp.message()
async def handle_messages(message: types.Message):
    if message.text == "/start":
        await message.answer("Вітаємо у нашому магазині! Оберіть дію:", reply_markup=main_keyboard)
    elif message.text == "Каталог":
        await message.answer("Ось каталог товарів:\n1. Товар A\n2. Товар B\n3. Товар C")
    elif message.text == "Кошик":
        await message.answer("Ваш кошик порожній.")
    else:
        await message.answer("Невідома команда.")


# --- Webhook endpoint ---
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return {"ok": True}


# --- Startup / Shutdown ---
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
import logging
import os

# --- Логування ---
logging.basicConfig(level=logging.INFO)

# --- Дані бота ---
TOKEN = os.getenv("BOT_TOKEN")  # або встав прямо токен
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://shop-x54i.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()

# --- Кнопки ---
def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Створити наступний квиток", callback_data="next_ticket")],
    ])
    return keyboard

# --- /start ---
@dp.message(Command(commands=["start"]))
async def start_handler(message: Message):
    await message.answer("Привіт! Бот готовий 🚀", reply_markup=main_menu_keyboard())

# --- Обробка кнопки ---
@dp.callback_query(lambda c: c.data == "next_ticket")
async def next_ticket_handler(callback_query: types.CallbackQuery):
    await callback_query.message.answer("Створюю наступний квиток...")
    # --- Тут вставляй свій код генерації PDF ---
    await callback_query.answer()  # закриваємо "loading" на кнопці

# --- Webhook endpoint ---
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)  # Передаємо bot і update
    return {"ok": True}

# --- FastAPI старт ---
@app.on_event("startup")
async def on_startup():
    # Встановлюємо webhook на Telegram
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

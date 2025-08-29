# app.py
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.executor import start_webhook
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"
PORT = int(os.environ.get("PORT", 10000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()


# --- Keyboards ---
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Каталог"), KeyboardButton(text="Кошик")]
    ],
    resize_keyboard=True
)

# --- Handlers ---
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Вітаємо у нашому магазині! Оберіть дію:",
        reply_markup=main_keyboard
    )


@dp.message_handler(lambda m: m.text == "Каталог")
async def show_catalog(message: types.Message):
    # Тут можна вставити логіку каталогу
    await message.answer("Ось каталог товарів:\n1. Товар A\n2. Товар B\n3. Товар C")


@dp.message_handler(lambda m: m.text == "Кошик")
async def show_cart(message: types.Message):
    # Тут можна вставити логіку кошика
    await message.answer("Ваш кошик порожній.")


# --- FastAPI webhook endpoint ---
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
    await bot.close()

# app.py
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
import logging
import os

# Логування
logging.basicConfig(level=logging.INFO)

# Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")  # або встав свій токен прямо

# Ініціалізація бота та диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ініціалізація FastAPI
app = FastAPI()

# --- Приклад хендлерів ---
@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привіт! Бот запущений через webhook 🚀")

# --- Webhook endpoint ---
@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != BOT_TOKEN:
        return {"status": "unauthorized"}

    update_data = await request.json()
    update = types.Update(**update_data)  # конвертуємо dict у Update

    try:
        # feed_update тепер потребує bot і update
        await dp.feed_update(bot=bot, update=update)
    except Exception as e:
        logging.error(f"Помилка webhook: {e}")

    return {"ok": True}

# --- Запуск при локальному тестуванні ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)

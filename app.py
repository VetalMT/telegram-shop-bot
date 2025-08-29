# app.py
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
import logging
import os

# ---------------------
# Налаштування
# ---------------------
API_TOKEN = os.getenv("BOT_TOKEN")  # Твій токен
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

app = FastAPI()

# ---------------------
# Основні хендлери
# ---------------------

@dp.message()
async def echo_handler(message):
    # Тут простий приклад: бот повторює повідомлення користувача
    await message.answer(f"Ти написав: {message.text}")

# ---------------------
# Webhook endpoint
# ---------------------
@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        update = Update(**data)
        # aiogram v3: feed_update відправляє оновлення до диспетчера
        await dp.feed_update(update=update)
        return {"status": "ok"}
    except Exception as e:
        logging.exception("Помилка webhook:")
        return {"status": "error", "detail": str(e)}

# ---------------------
# Root для перевірки сервісу
# ---------------------
@app.get("/")
async def root():
    return {"status": "Bot is running"}

# ---------------------
# Shutdown cleanup
# ---------------------
@app.on_event("shutdown")
async def shutdown():
    await bot.session.close()

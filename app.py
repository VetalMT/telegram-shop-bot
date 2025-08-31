import logging
import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
import asyncio

from db import engine, Base

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

app = FastAPI()

@app.on_event("startup")
async def startup():
    # створюємо таблиці
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # встановлюємо webhook
    webhook_url = f"{os.getenv('RENDER_EXTERNAL_URL')}/webhook/{TOKEN}"
    await bot.set_webhook(webhook_url)
    logging.info(f"✅ Webhook встановлено: {webhook_url}")


@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != TOKEN:
        return {"error": "Invalid token"}

    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.get("/")
async def root():
    return {"message": "✅ API працює на Render!"}


# Приклад команди
@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("Привіт! 👋 Бот працює через webhook 🚀")

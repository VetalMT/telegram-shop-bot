import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from config import BOT_TOKEN
from handlers_user import start_handler, catalog_handler, cart_handler
from handlers_admin import admin_start_handler
from db import engine, Base

logging.basicConfig(level=logging.INFO)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

app = FastAPI()

# --- Реєстрація хендлерів ---
dp.message.register(start_handler, Command(commands=["start"]))
dp.message.register(catalog_handler, lambda m: m.text=="Каталог")
dp.message.register(cart_handler, lambda m: m.text=="Кошик")
dp.message.register(admin_start_handler, lambda m: m.text in ["Додати товар","Видалити товар","Переглянути товари"])

# --- Webhook ---
@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != BOT_TOKEN:
        return {"error":"invalid token"}
    update = types.Update(**await request.json())
    await dp.feed_update(bot=bot, update=update)
    return {"ok": True}

# --- Ініціалізація бази ---
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logging.info("База даних готова.")

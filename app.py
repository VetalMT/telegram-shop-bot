import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.bot import DefaultBotProperties
from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Наприклад: https://your-app.onrender.com

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

app = FastAPI()

# Товари магазину
PRODUCTS = {
    "apple": {"name": "🍎 Яблуко", "price": 5},
    "banana": {"name": "🍌 Банан", "price": 3},
    "orange": {"name": "🍊 Апельсин", "price": 4},
}

# Генерація меню
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    for key, product in PRODUCTS.items():
        kb.add(InlineKeyboardButton(f"{product['name']} - {product['price']} грн", callback_data=f"buy_{key}"))
    kb.add(InlineKeyboardButton("🎫 Створити наступний товар", callback_data="restart"))
    return kb

# Старт
@dp.message()
async def start(message: types.Message):
    await message.answer("Ласкаво просимо до магазину! Оберіть товар:", reply_markup=main_menu())

# Обробка кнопок
@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    data = callback.data
    if data.startswith("buy_"):
        key = data[4:]
        product = PRODUCTS.get(key)
        if product:
            await callback.message.answer(
                f"Ви обрали {product['name']} за {product['price']} грн.\nДякуємо за покупку! ✅"
            )
        await callback.answer()
    elif data == "restart":
        await callback.message.answer("Оберіть товар знову:", reply_markup=main_menu())
        await callback.answer()

# Webhook endpoint
@app.post(f"/webhook/{BOT_TOKEN}")
async def webhook(request: Request):
    body = await request.json()
    update = types.Update(**body)
    await dp.process_update(update)
    return {"ok": True}

# Встановлення Webhook на старті
@app.on_event("startup")
async def on_startup():
    await bot.delete_webhook()
    webhook_url = f"{WEBHOOK_URL}/webhook/{BOT_TOKEN}"
    await bot.set_webhook(webhook_url)
    logging.info(f"Webhook встановлено на {webhook_url}")

# Закриття сесії бота
@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

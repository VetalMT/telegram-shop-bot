import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.bot import DefaultBotProperties
from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # Наприклад: https://shop-x54i.onrender.com

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

app = FastAPI()

# Простий каталог товарів
PRODUCTS = {
    "apple": {"name": "🍎 Яблуко", "price": 5},
    "banana": {"name": "🍌 Банан", "price": 3},
}

# Головне меню клієнта
def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📦 Каталог", callback_data="show_catalog"),
        InlineKeyboardButton("🛒 Кошик", callback_data="show_cart")
    )
    return kb

# Меню каталогу
def catalog_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    for key, prod in PRODUCTS.items():
        kb.add(InlineKeyboardButton(f"{prod['name']} - {prod['price']} грн", callback_data=f"buy_{key}"))
    kb.add(InlineKeyboardButton("🔙 Назад", callback_data="back_main"))
    return kb

# Простий кошик (тимчасовий, на сесію)
CART = {}

# Старт
@dp.message()
async def start(message: types.Message):
    CART[message.from_user.id] = []
    await message.answer("Ласкаво просимо до магазину! Оберіть дію:", reply_markup=main_menu())

# Обробка кнопок
@dp.callback_query()
async def handle_buttons(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data

    if data == "show_catalog":
        await callback.message.answer("Оберіть товар з каталогу:", reply_markup=catalog_menu())
    elif data == "show_cart":
        cart_items = CART.get(user_id, [])
        if not cart_items:
            text = "Ваш кошик порожній 🛒"
        else:
            text = "Ваш кошик:\n" + "\n".join(cart_items)
        await callback.message.answer(text, reply_markup=main_menu())
    elif data.startswith("buy_"):
        key = data[4:]
        product = PRODUCTS.get(key)
        if product:
            CART.setdefault(user_id, []).append(f"{product['name']} - {product['price']} грн")
            await callback.message.answer(f"✅ {product['name']} додано до кошика!")
    elif data == "back_main":
        await callback.message.answer("Головне меню:", reply_markup=main_menu())

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

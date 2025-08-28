import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message
from aiohttp import web
from db import get_products, add_to_cart, get_cart

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"https://твій_сайт.onrender.com{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Команда старт
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привіт! Це магазин. Напишіть /products для перегляду товарів.")

# Перегляд продуктів
@dp.message(Command("products"))
async def cmd_products(message: Message):
    products = await get_products()
    for p in products:
        text = f"<b>{p['name']}</b>\n{p['description']}\nЦіна: {p['price']}₴"
        keyboard = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Додати в кошик", callback_data=f"add_{p['id']}")
        )
        await message.answer(text, reply_markup=keyboard)

# Обробка кнопок
@dp.callback_query()
async def callbacks(query: types.CallbackQuery):
    data = query.data
    if data.startswith("add_"):
        product_id = int(data.split("_")[1])
        await add_to_cart(query.from_user.id, product_id)
        await query.answer("Додано в кошик!")

# Перегляд кошика
@dp.message(Command("cart"))
async def cmd_cart(message: Message):
    cart = await get_cart(message.from_user.id)
    if not cart:
        await message.answer("Ваш кошик порожній.")
        return
    text = "Ваш кошик:\n\n"
    total = 0
    for item in cart:
        text += f"{item['name']} x{item['qty']} — {item['price']*item['qty']}₴\n"
        total += item['price']*item['qty']
    text += f"\n<b>Разом: {total}₴</b>"
    await message.answer(text)

# Webhook для Render
async def handle(request):
    update = types.Update(**await request.json())
    await dp.feed_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)

if __name__ == "__main__":
    from aiohttp import web
    port = int(os.getenv("PORT", 10000))
    logging.info("Starting app...")
    web.run_app(app, host="0.0.0.0", port=port)

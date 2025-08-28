import os
import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from db import init_db, get_products, add_to_cart, get_cart, create_order, delete_product

logging.basicConfig(level=logging.INFO)

API_TOKEN = os.getenv("BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")

WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"https://telegram-shop-bot-z03b.onrender.com{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 8000))

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# ------------------- Хендлери -------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привіт! Це Telegram Shop Bot 🛒")

@dp.message(Command("products"))
async def cmd_products(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("Поки що немає товарів 😔")
        return
    msg = ""
    for p in products:
        pid, name, desc, price, photo_id = p
        msg += f"<b>{name}</b>\n{desc}\nЦіна: {price}₴\nID: {pid}\n\n"
    await message.answer(msg)

@dp.message()
async def add_product_to_cart(message: types.Message):
    text = message.text
    if text.startswith("add "):
        try:
            product_id = int(text.split()[1])
            await add_to_cart(message.from_user.id, product_id)
            await message.answer(f"✅ Товар {product_id} додано до корзини")
        except Exception as e:
            await message.answer(f"❌ Помилка: {e}")

@dp.message(Command("cart"))
async def show_cart(message: types.Message):
    items = await get_cart(message.from_user.id)
    if not items:
        await message.answer("Ваша корзина порожня 🛒")
        return
    msg = "<b>Ваша корзина:</b>\n\n"
    for i in items:
        msg += f"{i['name']} x{i['qty']} — {i['price']}₴\n"
    total = sum(i['qty']*i['price'] for i in items)
    msg += f"\n<b>Разом: {total}₴</b>"
    await message.answer(msg)

@dp.message(Command("order"))
async def make_order(message: types.Message):
    # Тестові дані для прикладу
    order_id = await create_order(message.from_user.id, "Імʼя Прізвище", "0991234567", "м. Київ, вул. Тестова 1")
    if order_id:
        await message.answer(f"✅ Замовлення #{order_id} створено!")
    else:
        await message.answer("❌ У вас порожня корзина")

# ------------------- Webhook -------------------

async def on_startup(app: web.Application):
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()

async def handle(request: web.Request):
    if request.match_info.get('token') != API_TOKEN:
        return web.Response(status=403)
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=PORT)

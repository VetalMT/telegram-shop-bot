import os
import logging
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from databases import Database
from sqlalchemy import MetaData, Table, Column, Integer, String, Float

# ================== Налаштування логів ==================
logging.basicConfig(level=logging.INFO)

# ================== Завантаження змінних ==================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_NAME = os.getenv("DB_NAME")

WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"

# ================== Підключення бота ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== Підключення бази даних ==================
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
database = Database(DATABASE_URL)
metadata = MetaData()

# ================== Таблиці ==================
products = Table(
    "products",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("description", String),
    Column("price", Float),
    Column("stock", Integer, default=0)
)

orders = Table(
    "orders",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String),
    Column("product_id", Integer),
    Column("quantity", Integer, default=1),
    Column("status", String, default="pending")
)

# ================== Хендлери ==================

@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message):
    await message.answer("Ласкаво просимо до нашого магазину! Використовуйте /products для перегляду товарів.")

@dp.message(Command(commands=["products"]))
async def cmd_products(message: types.Message):
    query = products.select()
    items = await database.fetch_all(query)
    if not items:
        await message.answer("Товари відсутні.")
        return

    for item in items:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Купити", callback_data=f"buy:{item['id']}")]
        ])
        await message.answer(f"{item['name']}\n{item['description']}\nЦіна: {item['price']} грн\nНа складі: {item['stock']}", reply_markup=kb)

@dp.callback_query(lambda c: c.data and c.data.startswith("buy:"))
async def process_buy(callback_query: CallbackQuery):
    product_id = int(callback_query.data.split(":")[1])
    query = products.select().where(products.c.id == product_id)
    item = await database.fetch_one(query)
    if not item or item['stock'] <= 0:
        await callback_query.message.answer("Цей товар закінчився.")
        return

    await database.execute(
        orders.insert().values(user_id=str(callback_query.from_user.id),
                               product_id=product_id,
                               quantity=1)
    )
    await database.execute(
        products.update().where(products.c.id == product_id).values(stock=item['stock'] - 1)
    )
    await callback_query.message.answer("Товар додано до замовлень. Очікуйте на підтвердження.")

@dp.message(Command(commands=["orders"]))
async def cmd_orders(message: types.Message):
    query = orders.select().where(orders.c.user_id == str(message.from_user.id))
    user_orders = await database.fetch_all(query)
    if not user_orders:
        await message.answer("У вас немає замовлень.")
        return

    text = "Ваші замовлення:\n"
    for o in user_orders:
        product = await database.fetch_one(products.select().where(products.c.id == o['product_id']))
        text += f"{product['name']} x{o['quantity']} - Статус: {o['status']}\n"
    await message.answer(text)

@dp.message(Command(commands=["add_product"]))
async def cmd_add_product(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Ви не адмін.")
        return
    try:
        args = message.text.split(maxsplit=4)
        _, name, description, price, stock = args
        await database.execute(products.insert().values(
            name=name,
            description=description,
            price=float(price),
            stock=int(stock)
        ))
        await message.answer("Товар додано.")
    except Exception as e:
        await message.answer(f"Помилка: {e}")

# ================== Webhook ==================
async def handle_webhook(request: web.Request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return web.Response(text="ok")

# ================== Запуск ==================
async def on_startup(app):
    await database.connect()
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()
    await database.disconnect()

app = web.Application()
app.router.add_post("/webhook", handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 10000)))
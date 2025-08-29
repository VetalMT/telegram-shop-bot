import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web
import asyncio
import os

from database import database, products, orders
from sqlalchemy import select

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Запуск бази
async def on_startup(app):
    await database.connect()
    logging.info("✅ Database connected")
    
async def on_shutdown(app):
    await database.disconnect()
    logging.info("❌ Database disconnected")

# Список товарів
@dp.message(Command("start"))
async def start(message: types.Message):
    query = products.select()
    items = await database.fetch_all(query)
    
    kb_builder = InlineKeyboardBuilder()
    for item in items:
        kb_builder.button(
            text=f"{item['name']} - {item['price']}₴",
            callback_data=f"buy:{item['id']}"
        )
    kb_builder.adjust(1)
    
    await message.answer("Виберіть товар:", reply_markup=kb_builder.as_markup())

# Обробка кнопок
@dp.callback_query(lambda c: c.data and c.data.startswith("buy:"))
async def buy(callback: types.CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await database.execute(
        orders.insert().values(user_id=str(callback.from_user.id), product_id=product_id, quantity=1)
    )
    await callback.answer("✅ Товар додано до замовлень")

# Вебхук для Render
async def handle_webhook(request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return web.Response(text="ok")

app = web.Application()
app.router.add_post("/webhook", handle_webhook)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 10000)))
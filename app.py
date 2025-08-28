import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Update
from aiogram.client.bot import DefaultBotProperties
from db import init_db, get_products, add_product, delete_product, add_to_cart, get_cart, create_order

API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("❌ Не вказано API_TOKEN в змінних оточення!")

# --- Логування ---
logging.basicConfig(level=logging.INFO)

# --- Бот і диспетчер ---
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# --- Ініціалізація бази ---
async def on_startup():
    await init_db()
    logging.info("✅ DB initialized")

# --- Простий хендлер старту ---
@dp.message(F.text == "/start")
async def cmd_start(message):
    await message.answer("Привіт! Це магазин бота. Використовуй меню для навігації.")

# --- Хендлер для перегляду продуктів ---
@dp.message(F.text == "🛍️ Переглянути товари")
async def show_products(message):
    products = await get_products()
    if not products:
        await message.answer("Товари відсутні.")
        return
    text = "\n".join([f"{p[1]} — {p[3]} грн" for p in products])
    await message.answer(f"Список товарів:\n{text}")

# --- Webhook handler для Render ---
async def handle(request: web.Request):
    try:
        update = Update(**await request.json())
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.exception(e)
    return web.Response(text="OK")

# --- Запуск aiohttp серверу ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))  # Render дає PORT
    app = web.Application()
    app.router.add_post(f"/webhook/{API_TOKEN}", handle)
    app.on_startup.append(lambda app: on_startup())
    logging.info(f"🚀 Running on 0.0.0.0:{port}")
    web.run_app(app, host="0.0.0.0", port=port)

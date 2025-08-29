import os
import logging
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдений у змінних середовища!")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ==============================
# 🗄️ БАЗА
# ==============================
def init_db():
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    """)
    conn.commit()
    conn.close()

# ==============================
# ХЕНДЛЕРИ
# ==============================
@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Категорії"))
    await message.answer("Ласкаво просимо в магазин! Оберіть дію:", reply_markup=kb)

# ==============================
# 🚀 AIOHTTP Web App
# ==============================
async def on_startup(app: web.Application):
    init_db()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook set: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    logging.info("🛑 Webhook deleted")

def setup_app() -> web.Application:
    app = web.Application()
    # webhook handler
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(setup_app(), host="0.0.0.0", port=port)
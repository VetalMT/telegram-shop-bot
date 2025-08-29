import os
import logging
import sqlite3
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)

# ==============================
# 🔑 ТУТ БУДЕ ТВІЙ ТОКЕН
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдений у змінних середовища!")

# ==============================
# 🌐 Webhook
# ==============================
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# ==============================
# 🗄️ БАЗА (магазин)
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

def get_categories():
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_products(category_id):
    conn = sqlite3.connect("shop.db")
    cur = conn.cursor()
    cur.execute("SELECT name, price FROM products WHERE category_id=?", (category_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

# ==============================
# 🛒 ХЕНДЛЕРИ
# ==============================
@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛍 Категорії"))
    await message.answer("Ласкаво просимо в магазин! Оберіть дію:", reply_markup=kb)

@dp.message(F.text == "🛍 Категорії")
async def show_categories(message: Message):
    cats = get_categories()
    if not cats:
        await message.answer("Категорій немає ❌")
        return
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    for cid, name in cats:
        kb.add(KeyboardButton(f"📦 {cid}:{name}"))
    await message.answer("Оберіть категорію:", reply_markup=kb)

@dp.message(F.text.startswith("📦"))
async def show_products(message: Message):
    try:
        cid = int(message.text.split(":")[0].replace("📦 ", ""))
        products = get_products(cid)
        if not products:
            await message.answer("Товарів немає ❌")
            return
        text = "🛒 <b>Товари:</b>\n\n"
        for name, price in products:
            text += f"• {name} — {price:.2f} грн\n"
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Помилка: {e}")

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
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    dp.workflow_data["AIOHTTP_APP"] = app
    app.router.add_post(WEBHOOK_PATH, dp._webhook_view(bot))  # для aiogram 3.7+
    return app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    web.run_app(setup_app(), host="0.0.0.0", port=port)
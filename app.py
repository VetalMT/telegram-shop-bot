import os
import logging
from aiohttp import web
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler

# -----------------------
# Завантаження токена
# -----------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено у .env")

# -----------------------
# Налаштування логів
# -----------------------
logging.basicConfig(level=logging.INFO)

# -----------------------
# Ініціалізація бота
# -----------------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# -----------------------
# Головне меню (категорії)
# -----------------------
main_kb = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text="📱 Телефони"),
         types.KeyboardButton(text="💻 Ноутбуки")],
        [types.KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

# -----------------------
# Тимчасове сховище (без БД)
# -----------------------
CART = {}

# -----------------------
# Хендлери
# -----------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привіт 👋 Це тестовий магазин!\nОберіть категорію товарів нижче:",
        reply_markup=main_kb
    )

# Вибір категорії
@dp.message(F.text == "📱 Телефони")
async def show_phones(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="iPhone 14 - 1000$", callback_data="add_iphone")],
        [types.InlineKeyboardButton(text="Samsung S23 - 900$", callback_data="add_samsung")]
    ])
    await message.answer("📱 Телефони:", reply_markup=kb)

@dp.message(F.text == "💻 Ноутбуки")
async def show_laptops(message: types.Message):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="MacBook Air - 1500$", callback_data="add_macbook")],
        [types.InlineKeyboardButton(text="Dell XPS - 1300$", callback_data="add_dell")]
    ])
    await message.answer("💻 Ноутбуки:", reply_markup=kb)

# Додавання товарів у корзину
@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    product_map = {
        "add_iphone": "iPhone 14 - 1000$",
        "add_samsung": "Samsung S23 - 900$",
        "add_macbook": "MacBook Air - 1500$",
        "add_dell": "Dell XPS - 1300$"
    }
    product = product_map.get(callback.data, "Невідомий товар")

    if user_id not in CART:
        CART[user_id] = []
    CART[user_id].append(product)

    await callback.answer("✅ Додано у корзину")
    await callback.message.edit_reply_markup(reply_markup=None)

# Перегляд корзини
@dp.message(F.text == "🛒 Корзина")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    if user_id not in CART or not CART[user_id]:
        await message.answer("Ваша корзина порожня 🛒")
    else:
        items = "\n".join(CART[user_id])
        await message.answer(f"🛒 Ваша корзина:\n\n{items}")

# -----------------------
# WEBHOOK
# -----------------------
WEBHOOK_PATH = "/webhook"
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL")  # Render дає URL
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

async def on_startup(app):
    if WEBHOOK_URL:
        await bot.set_webhook(WEBHOOK_URL)
        logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")
    else:
        logging.warning("⚠️ WEBHOOK_URL не знайдено")

async def on_shutdown(app):
    logging.info("♻️ Бот вимикається..")
    await bot.delete_webhook()
    await bot.session.close()

# -----------------------
# AIOHTTP APP
# -----------------------
def create_app():
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

# -----------------------
# Запуск
# -----------------------
if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

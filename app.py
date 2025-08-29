import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# -------------------
# 🔹 Логування
# -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------
# 🔹 Налаштування
# -------------------
API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    logger.warning("⚠️ API_TOKEN не знайдено у змінних середовища! Перевір Render Dashboard → Environment Variables")

WEBHOOK_HOST = "https://shop-x54i.onrender.com"   # 🔹 заміни на свій Render URL
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# -------------------
# 🔹 Категорії товарів
# -------------------
CATEGORIES = {
    "electronics": {
        "title": "📱 Електроніка",
        "items": ["Телефон", "Ноутбук", "Навушники"]
    },
    "clothes": {
        "title": "👕 Одяг",
        "items": ["Футболка", "Куртка", "Кросівки"]
    },
    "food": {
        "title": "🍔 Їжа",
        "items": ["Бургер", "Піца", "Хот-дог"]
    }
}

# -------------------
# 🔹 Команди
# -------------------
@dp.message(F.text == "/start")
async def start_cmd(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=cat["title"], callback_data=f"cat:{key}")]
        for key, cat in CATEGORIES.items()
    ])
    await message.answer("👋 Вітаю у магазині!\nОберіть категорію:", reply_markup=kb)

# -------------------
# 🔹 Обробка категорій
# -------------------
@dp.callback_query(F.data.startswith("cat:"))
async def category_handler(callback: CallbackQuery):
    cat_key = callback.data.split(":")[1]
    category = CATEGORIES.get(cat_key)

    if not category:
        await callback.answer("❌ Категорія не знайдена", show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=item, callback_data=f"item:{cat_key}:{item}")]
            for item in category["items"]
        ]
    )
    await callback.message.edit_text(f"📦 {category['title']}:\nОберіть товар:", reply_markup=kb)

# -------------------
# 🔹 Обробка товарів
# -------------------
@dp.callback_query(F.data.startswith("item:"))
async def item_handler(callback: CallbackQuery):
    _, cat_key, item = callback.data.split(":")
    await callback.message.edit_text(
        f"✅ Ви обрали: <b>{item}</b>\n\n"
        f"Категорія: {CATEGORIES[cat_key]['title']}\n"
        f"💰 Ціна: 100₴ (тестова)"
    )

# -------------------
# 🔹 Webhook сервер
# -------------------
async def on_startup(app: web.Application):
    if not API_TOKEN:
        raise RuntimeError("❌ API_TOKEN не завантажено. Додай у Render → Environment Variables!")

    # Скидаємо старий вебхук
    await bot.delete_webhook()
    # Ставимо новий
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.session.close()

def setup_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, dp.webhook_handler())
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

# -------------------
# 🔹 Запуск
# -------------------
if __name__ == "__main__":
    web.run_app(setup_app(), host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
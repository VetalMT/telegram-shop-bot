import logging
import os
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiohttp import web

# наші модулі
from handlers_admin import admin_router
from handlers_user import user_router
from handlers_shop import shop_router
from db import init_db
from keyboards import shop_kb, admin_kb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")

# 🛡️ ID адміністратора
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
if not ADMIN_ID:
    raise ValueError("❌ Не вказано ADMIN_ID в змінних оточення!")

# 🌍 Webhook URL (Render виставляє RENDER_EXTERNAL_URL)
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
if not RENDER_EXTERNAL_URL:
    raise ValueError("❌ Не вказано RENDER_EXTERNAL_URL в змінних оточення!")

WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

# ================== Налаштування бота ==================
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)

# ================== Клавіатури (для локального використання стартових повідомлень) ==================
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Каталог"), KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

# ================== Роутери ==================
dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(shop_router)

# ================== Адмін / старт ==================
@dp.message_handler(commands=["start"])
async def start_handler(message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Вітаю, адміністратор!", reply_markup=admin_kb)
    else:
        await message.answer("Вітаю у магазині!", reply_markup=shop_kb)

# ================== Webhook ==================
async def handle_webhook(request: web.Request):
    update = await request.json()
    # Feed update into dispatcher
    await dp.feed_webhook_update(bot, update)
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    logger.info("Запуск: ініціалізація БД...")
    await init_db()
    # Прописати вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("⚠️ Бот зупиняється...")
    await bot.delete_webhook()
    await bot.session.close()
    await storage.close()

# ================== Запуск ==================
def main():
    port = int(os.getenv("PORT", 10000))
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    # опційно простий healthcheck на /
    async def health(request: web.Request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

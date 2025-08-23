import logging
import os

from aiogram import Bot, Dispatcher
from aiohttp import web

from db import init_db
from handlers_admin import setup_admin_handlers
from handlers_user import user_router

# 🔧 Логування
logging.basicConfig(level=logging.INFO)

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")

# 🌍 URL твого додатку (Render надає https://...)
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL")
if not RENDER_URL:
    raise ValueError("❌ Не вказано RENDER_EXTERNAL_URL!")
WEBHOOK_URL = f"{RENDER_URL}/webhook"

# ================== Налаштування бота ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ================== Підключення хендлерів ==================
setup_admin_handlers(dp)          # адмін-панель
dp.include_router(user_router)    # користувачі (каталог/кошик/замовлення)

# ================== Webhook ==================
async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def on_startup(app: web.Application):
    # 1) Ініціалізація БД (створить таблиці, якщо їх немає)
    await init_db()
    logging.info("🗄️ База даних ініціалізована")

    # 2) Ставимо вебхук
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("⚠️ Бот зупиняється...")
    await bot.session.close()

# ================== Запуск ==================
def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

if __name__ == "__main__":
    main()

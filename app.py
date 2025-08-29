import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# 🔹 Імпорт роутерів
from handlers_user import user_router
from handlers_admin import admin_router
from handlers_shop import shop_router
from db import init_db

logging.basicConfig(level=logging.INFO)

# ==============================
# 🔑 BOT TOKEN
# ==============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдений у змінних середовища!")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# 🔹 Підключення хендлерів
dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(shop_router)

# ==============================
# 🚀 AIOHTTP Web App
# ==============================
async def on_startup(app: web.Application):
    await init_db()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook set: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    logging.info("🛑 Webhook deleted")

def setup_app() -> web.Application:
    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    web.run_app(setup_app(), host="0.0.0.0", port=port)

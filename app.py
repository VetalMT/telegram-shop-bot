import logging
import os
from aiohttp import web

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, RENDER_EXTERNAL_URL
from db import init_db
from handlers_admin import register_admin_handlers
from handlers_user import register_user_handlers

# ================== Логування ==================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== Перевірка змінних оточення ==================
if not BOT_TOKEN:
    raise ValueError("❌ Не вказано BOT_TOKEN в змінних оточення!")
if not ADMIN_ID:
    raise ValueError("❌ Не вказано ADMIN_ID в змінних оточення!")
if not RENDER_EXTERNAL_URL:
    raise ValueError("❌ Не вказано RENDER_EXTERNAL_URL в змінних оточення!")

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL.rstrip('/')}{WEBHOOK_PATH}"

# ================== Ініціалізація бота/диспетчера ==================
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()  # можна замінити на RedisStorage2 при потребі
dp = Dispatcher(bot, storage=storage)

# Реєструємо всі хендлери
register_admin_handlers(dp)
register_user_handlers(dp)

# ================== AIOHTTP Web App ==================
async def handle_webhook(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="Bad Request: invalid JSON")

    update = types.Update(**data)
    await dp.process_updates([update])
    return web.Response(text="OK")

async def health(request: web.Request) -> web.Response:
    return web.Response(text="OK")

async def on_startup(app: web.Application):
    logger.info("🔧 Стартуємо: ініціалізація БД та встановлення webhook...")
    await init_db()
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    logger.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("⚠️ Зупинка бота...")
    await bot.session.close()
    await storage.close()
    await storage.wait_closed()
    logger.info("👋 До зустрічі!")

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    host = "0.0.0.0"
    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host=host, port=port)

if __name__ == "__main__":
    main()

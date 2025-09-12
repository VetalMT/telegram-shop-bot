import logging
import os
import asyncio
import json
from aiohttp import web, ClientSession

from aiogram import Bot, Dispatcher
from aiogram.types import Update, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# свої модулі
from handlers_user import user_router
from handlers_admin import admin_router
from db import init_db, count_products
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------
BOT_TOKEN = config.BOT_TOKEN
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не встановлений!")

WEBHOOK_HOST = config.WEBHOOK_HOST
if not WEBHOOK_HOST:
    raise RuntimeError("WEBHOOK_HOST / RENDER_EXTERNAL_URL не встановлений!")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# Aiogram
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Підключаємо роутери
dp.include_router(user_router)
dp.include_router(admin_router)

# -----------------------
# startup / shutdown
# -----------------------
async def on_startup(app: web.Application):
    logger.info("🚀 on_startup: ініціалізація БД...")
    try:
        await init_db()
        logger.info("✅ DB initialized.")
    except Exception as e:
        logger.exception("Помилка init_db(): %s", e)

    # Спроба встановити webhook і логування результату
    try:
        ok = await bot.set_webhook(WEBHOOK_URL)
        logger.info("🌍 set_webhook result: %s    url=%s", ok, WEBHOOK_URL)
    except Exception as e:
        logger.exception("❌ Помилка при set_webhook(): %s", e)

    # Встановимо команди (не обов'язково)
    try:
        commands = [
            BotCommand(command="/start", description="Почати роботу"),
            BotCommand(command="/help", description="Допомога"),
        ]
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.warning("Не вдалось set_my_commands: %s", e)

async def on_shutdown(app: web.Application):
    logger.info("⚠️ on_shutdown: закриваємо сесію бота...")
    try:
        await bot.session.close()
    except Exception as e:
        logger.warning("Помилка при закритті сесії: %s", e)
    logger.info("Завершено.")

# -----------------------
# Webhook handler
# -----------------------
async def handle_webhook(request: web.Request):
    try:
        data = await request.json()
    except Exception as e:
        logger.exception("Неможливо прочитати JSON з webhook: %s", e)
        return web.Response(status=400, text="Bad Request")

    try:
        # Валідуємо апдейт і прокидуємо в диспетчер
        update = Update.model_validate(data)
        # feed_update / feed_webhook_update difference across aiogram versions — feed_update підходить тут
        await dp.feed_update(bot, update)
        logger.debug("✅ Update processed.")
    except Exception as e:
        logger.exception("❌ Помилка обробки апдейту: %s", e)
    return web.Response(text="OK")

# -----------------------
# Debug endpoints
# -----------------------
async def debug_webhook_info(request: web.Request):
    """Повертає getWebhookInfo від Telegram (корисно для діагностики)."""
    token = BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/getWebhookInfo"
    try:
        async with ClientSession() as sess:
            async with sess.get(url, timeout=10) as r:
                text = await r.text()
                try:
                    data = json.loads(text)
                except Exception:
                    data = {"raw": text}
                return web.json_response(data)
    except Exception as e:
        logger.exception("Помилка підключення до Telegram API: %s", e)
        return web.json_response({"error": str(e)})

async def debug_db_count(request: web.Request):
    """Повертає кількість товарів у БД."""
    try:
        c = await count_products()
        return web.json_response({"products_count": c})
    except Exception as e:
        logger.exception("Помилка debug_db_count: %s", e)
        return web.json_response({"error": str(e)})

# -----------------------
def create_app():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)
    app.router.add_get("/", lambda r: web.Response(text="OK"))
    app.router.add_get("/debug/webhook_info", debug_webhook_info)
    app.router.add_get("/debug/db_count", debug_db_count)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    return app

# -----------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    web.run_app(create_app(), host="0.0.0.0", port=port)

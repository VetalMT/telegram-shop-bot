import os
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# імпорти з твоїх файлів у корені
from handlers_admin import admin_router
from handlers_shop import shop_router
from handlers_user import user_router
from db import init_db
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = config.BOT_TOKEN
if not BOT_TOKEN:
    raise RuntimeError("❌ Не вказано BOT_TOKEN в змінних оточення!")

WEBHOOK_HOST = config.WEBHOOK_HOST
if not WEBHOOK_HOST:
    raise RuntimeError("❌ Не вказано WEBHOOK_HOST або RENDER_EXTERNAL_URL у змінних оточення!")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# Aiogram objects
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Роутери
dp.include_router(admin_router)
dp.include_router(shop_router)
dp.include_router(user_router)


async def handle_webhook(request: web.Request):
    """Приймаємо update від Telegram (JSON) і передаємо диспетчеру."""
    try:
        update = await request.json()
    except Exception as e:
        logger.exception("Failed to parse request JSON: %s", e)
        return web.Response(status=400, text="Bad Request")
    await dp.feed_webhook_update(bot=bot, update=update)
    return web.Response(text="OK")


async def on_startup(app: web.Application):
    logger.info("🚀 Startup: ініціалізую БД...")
    await init_db()
    logger.info("🌍 Встановлюю webhook: %s", WEBHOOK_URL)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook встановлено.")


async def on_shutdown(app: web.Application):
    logger.info("⚠️ Shutdown: видаляю webhook і закриваю сесію...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.exception("Помилка при видаленні webhook: %s", e)
    try:
        await bot.session.close()
    except Exception:
        pass
    logger.info("Завершено.")


def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    async def health(request: web.Request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", "8080"))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

import logging
import os
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# наші модулі (пакет handlers)
from handlers.admin import admin_router
from handlers.user import user_router
from handlers.shop import shop_router
from db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- ENV ----------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("❌ Не вказано BOT_TOKEN в змінних оточення!")

ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
if ADMIN_ID == 0:
    raise RuntimeError("❌ Не вказано ADMIN_ID в змінних оточення!")

# Повинен містити протокол, напр. https://my-app.onrender.com
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
if not WEBHOOK_HOST:
    raise RuntimeError("❌ Не вказано WEBHOOK_HOST в змінних оточення! (напр. https://mydomain.com)")

# Шлях вебхуку (додаємо токен у шлях для безпеки)
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# ---------------- Aiogram ----------------
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Роутери
dp.include_router(admin_router)
dp.include_router(user_router)
dp.include_router(shop_router)

# ---------------- Webhook handler ----------------
async def handle_webhook(request: web.Request):
    """Приймаємо update від Telegram (JSON) і передаємо його диспетчеру."""
    try:
        update = await request.json()
    except Exception as e:
        logger.exception("Failed to parse request JSON: %s", e)
        return web.Response(status=400, text="Bad Request")
    await dp.feed_webhook_update(bot=bot, update=update)
    return web.Response(text="OK")

# ---------------- Startup / Shutdown ----------------
async def on_startup(app: web.Application):
    logger.info("Запуск: ініціалізація БД...")
    await init_db()
    logger.info("Реєструю webhook: %s", WEBHOOK_URL)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook встановлено.")

async def on_shutdown(app: web.Application):
    logger.info("Зупинка бота: видаляю webhook і закриваю сесію...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        logger.exception("Помилка при видаленні webhook: %s", e)
    try:
        await bot.session.close()
    except Exception:
        pass
    logger.info("Завершено.")

# ---------------- Run app ----------------
def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    # healthcheck
    async def health(request: web.Request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", "8080"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

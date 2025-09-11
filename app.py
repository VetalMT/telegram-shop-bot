import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update, BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# наші модулі
from handlers_user import user_router
from handlers_admin import admin_router
from db import init_db
import config

# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
BOT_TOKEN = config.BOT_TOKEN
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не встановлений у environment variables!")

WEBHOOK_HOST = config.WEBHOOK_HOST
if not WEBHOOK_HOST:
    raise RuntimeError("WEBHOOK_HOST (або RENDER_EXTERNAL_URL) не встановлений у environment variables!")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST.rstrip('/')}{WEBHOOK_PATH}"

# -------------------------------
# Aiogram
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

# Підключаємо роутери (адмінка і користувачі)
dp.include_router(user_router)
dp.include_router(admin_router)

# -------------------------------
async def on_startup(app: web.Application):
    logger.info("🚀 on_startup: ініціалізація БД...")
    # Ініціалізуємо таблиці перед тим, як хендлери почнуть звертатись у БД
    await init_db()
    logger.info("🌍 Встановлюю webhook: %s", WEBHOOK_URL)
    await bot.set_webhook(WEBHOOK_URL)

    # команди бота
    commands = [
        BotCommand(command="/start", description="Почати роботу"),
        BotCommand(command="/help", description="Допомога"),
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        logger.warning("Не вдалось встановити команди: %s", e)
    logger.info("✅ on_startup завершено.")

async def on_shutdown(app: web.Application):
    logger.info("⚠️ on_shutdown: закриваю сесію бота...")
    # НЕ видаляємо webhook тут (щоб Telegram не "забув" URL після рестарту)
    try:
        await bot.session.close()
    except Exception:
        pass
    logger.info("Завершено.")

# Webhook handler
async def handle(request: web.Request):
    try:
        data = await request.json()
    except Exception as e:
        logger.exception("Неможливо прочитати JSON: %s", e)
        return web.Response(status=400, text="Bad Request")

    try:
        update = Update.model_validate(data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.exception("❌ Помилка обробки апдейту: %s", e)

    return web.Response(text="OK")

def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    # простий healthcheck
    async def health(request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    port = int(os.getenv("PORT", "10000"))
    web.run_app(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()

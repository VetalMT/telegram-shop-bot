import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web

from handlers_user import user_router
from handlers_admin import admin_router

# -------------------------------
# 🔧 Logging
# -------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------
# 🔧 Config
# -------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # https://shop-x54i.onrender.com
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())
dp.include_router(user_router)
dp.include_router(admin_router)


# -------------------------------
# 🔧 Startup & Shutdown
# -------------------------------
async def on_startup(app: web.Application):
    logger.info("🚀 Startup: ініціалізую БД...")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"🌍 Встановлюю webhook: {WEBHOOK_URL}")


async def on_shutdown(app: web.Application):
    logger.info("⚠️ Shutdown: видаляю webhook і закриваю сесію...")
    await bot.delete_webhook()
    await bot.session.close()


# -------------------------------
# 🔧 Aiogram bot handlers
# -------------------------------
async def set_commands():
    commands = [
        BotCommand(command="/start", description="Почати роботу"),
        BotCommand(command="/help", description="Допомога"),
    ]
    await bot.set_my_commands(commands)


# -------------------------------
# 🔧 Aiohttp web server
# -------------------------------
async def handle(request: web.Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()


def main():
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


if __name__ == "__main__":
    main()

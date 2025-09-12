import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT
from db import init_db
from handlers_admin import admin_router
from handlers_user import user_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    logger.info("🚀 on_startup: ініціалізація БД...")
    await init_db()
    logger.info("✅ DB initialized.")

    res = await bot.set_webhook(WEBHOOK_URL)
    logger.info("🌍 set_webhook result: %s    url=%s", res, WEBHOOK_URL)


async def on_shutdown(bot: Bot):
    logger.info("⚠️ on_shutdown: закриваємо сесію бота...")
    await bot.session.close()
    logger.info("Завершено.")


def main():
    bot = Bot(token=TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    # ✅ підключаємо роутери в правильному порядку
    dp.include_router(admin_router)
    dp.include_router(user_router)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{TOKEN}")
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)


if __name__ == "__main__":
    main()

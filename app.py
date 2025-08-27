import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from dotenv import load_dotenv

from handlers_user import user_router
from handlers_admin import admin_router

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Підключаємо всі роутери
dp.include_router(user_router)
dp.include_router(admin_router)


async def on_startup(bot: Bot):
    # Очищуємо старий вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    # Ставимо новий
    await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


async def main():
    app = web.Application()
    app["bot"] = bot

    # webhook handler
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
    setup_application(app, dp, bot=bot)

    # старти/стопи
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    asyncio.run(main())
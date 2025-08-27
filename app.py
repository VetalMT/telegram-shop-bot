import logging
import os
from aiogram import Bot, Dispatcher
from aiohttp import web

from handlers_admin import admin_router
from handlers_user import user_router
from db import init_db

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не знайдено в env!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


async def on_startup(app):
    init_db()
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await bot.set_webhook(os.getenv("WEBHOOK_URL"))


async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()


async def handle(request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()


def main():
    app = web.Application()
    app.router.add_post("/", handle)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, port=int(os.getenv("PORT", 8080)))


if __name__ == "__main__":
    main()
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, RENDER_EXTERNAL_URL, PORT
from handlers_admin import admin_router
from handlers_user import user_router
from db import init_db

logging.basicConfig(level=logging.INFO)

WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(admin_router)
dp.include_router(user_router)

async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()

async def on_startup(app: web.Application):
    await init_db()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logging.info("⚠️ Бот зупиняється...")
    await bot.session.close()

def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    async def health(request: web.Request):
        return web.Response(text="OK")
    app.router.add_get("/", health)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
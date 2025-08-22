import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from config import TOKEN, ADMIN_ID
from handlers_admin import setup_admin_handlers
from handlers_shop import setup_shop_handlers

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Підключаємо хендлери
setup_admin_handlers(dp)
setup_shop_handlers(dp)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("👋 Привіт! Це магазин-бот. Обери дію з меню.")


# --- Webhook handler ---
async def handle_webhook(request: web.Request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response()


# --- Startup / Shutdown ---
async def on_startup(app):
    # встановлюємо вебхук
    webhook_url = os.getenv("WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("❌ Не задано WEBHOOK_URL в Render ENV VARS")
    await bot.set_webhook(webhook_url)
    print(f"✅ Webhook встановлено: {webhook_url}")


async def on_shutdown(app):
    await bot.session.close()


def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))


if __name__ == "__main__":
    main()

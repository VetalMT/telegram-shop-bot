import logging
import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from db import init_db, add_product, get_products

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

if not BOT_TOKEN or not RENDER_EXTERNAL_URL:
    raise ValueError("Не вказано BOT_TOKEN або RENDER_EXTERNAL_URL")

WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/webhook"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ================= Handlers =================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Бот онлайн! Введи /products щоб переглянути товари.")


@dp.message(Command("products"))
async def products_handler(message: types.Message):
    products = get_products()
    if not products:
        await message.answer("Товари відсутні.")
    else:
        text = "\n".join([f"{p['id']}. {p['name']} - {p['price']}₴" for p in products])
        await message.answer(text)


# ================= Webhook =================
async def handle_webhook(request: web.Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()


async def on_startup(app: web.Application):
    # 1) Ініціалізуємо БД
    init_db()
    # 2) Встановлюємо webhook
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook встановлено: {WEBHOOK_URL}")


async def on_shutdown(app: web.Application):
    logging.info("Зупинка бота...")
    await bot.session.close()


def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.router.add_get("/", lambda request: web.Response(text="OK"))

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))


if __name__ == "__main__":
    main()
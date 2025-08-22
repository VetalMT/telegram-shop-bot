import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID, WEBHOOK_URL

# --- Ініціалізація бота та диспетчера ---
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Клавіатури (тимчасово прості приклади) ---
from keyboards import shop_kb, admin_kb

# --- Стартові команди ---
@dp.message(Command("start"))
async def cmd_start(message: Message):
    if str(message.from_user.id) == str(ADMIN_ID):
        await message.answer("👋 Привіт, адмін! Ось ваша панель.", reply_markup=admin_kb)
    else:
        await message.answer("👋 Привіт! Ласкаво просимо до магазину.", reply_markup=shop_kb)

# --- Обробка вебхука ---
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

# --- Старт сервера ---
async def on_startup(app):
    # встановлюємо вебхук для Telegram
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook встановлено на {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.session.close()
    print("Бот завершив роботу.")

# --- Головна функція ---
def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

if __name__ == "__main__":
    main()

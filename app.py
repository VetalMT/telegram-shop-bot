import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from aiogram.client.default import DefaultBotProperties

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================
# Налаштування
# =============================
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}{WEBHOOK_PATH}"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")  # замість parse_mode напряму
)
dp = Dispatcher()

# =============================
# Хендлери
# =============================
@dp.message()
async def echo_handler(message):
    await message.answer(f"Ти написав: {message.text}")

# =============================
# Webhook server
# =============================
async def handle_webhook(request: web.Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return web.Response()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)

# =============================
# Startup / Shutdown
# =============================
@app.on_startup
async def on_startup(app):
    logger.info("🚀 Startup: ініціалізую БД...")
    logger.info(f"🌍 Встановлюю webhook: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook встановлено.")

@app.on_shutdown
async def on_shutdown(app):
    logger.info("⚠️ Shutdown: закриваю сесію...")
    await bot.session.close()

# =============================
# Run app
# =============================
if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

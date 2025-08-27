import logging
from aiogram import Bot, Dispatcher
from aiogram.utils.executor import start_webhook
from config import BOT_TOKEN, RENDER_EXTERNAL_URL, PORT, ADMIN_ID
from db import init_db
from handlers_admin import register_admin
from handlers_user import register_user
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = PORT  # Render PORT

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# register handlers
register_admin(dp)
register_user(dp)

async def on_startup(dp):
    # init db
    await init_db()
    # set webhook
    await bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook set: %s", WEBHOOK_URL)

async def on_shutdown(dp):
    logging.info("Shutting down..")
    await bot.delete_webhook()
    await bot.close()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
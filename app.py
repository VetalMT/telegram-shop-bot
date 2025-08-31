import logging
import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

from handlers_user import register_user_handlers
from handlers_admin import register_admin_handlers
from db import init_db

# Завантажуємо .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def start_bot():
    logger.info("🚀 Запуск бота...")
    await init_db()  # ініціалізація бази
    register_user_handlers(dp)
    register_admin_handlers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("❌ Бот зупинений")

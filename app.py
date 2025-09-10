import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import Message

# імпорти оновлені під твою структуру
from handlers_admin import admin_router
from handlers_shop import shop_router
from handlers_user import user_router
from keyboards import menu_kb
import config

# Логування
logging.basicConfig(level=logging.INFO)


async def start_bot():
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # підключаємо хендлери
    dp.include_router(admin_router)
    dp.include_router(shop_router)
    dp.include_router(user_router)

    # простий тестовий хендлер, щоб перевірити чи бот відповідає
    @dp.message(commands=["start"])
    async def cmd_start(message: Message):
        await message.answer(
            "Привіт 👋! Бот працює.\n"
            "Меню доступне нижче 👇",
            reply_markup=menu_kb
        )

    # запуск бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот зупинений!")

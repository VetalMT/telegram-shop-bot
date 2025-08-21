import logging
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, ADMIN_ID
from keyboards import main_menu

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer("Ласкаво просимо до нашого магазину!", reply_markup=main_menu())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

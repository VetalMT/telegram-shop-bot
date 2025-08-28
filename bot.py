import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from db import init_db, get_connection

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ініціалізація БД
init_db()

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (user_id, username) VALUES (%s, %s) ON CONFLICT (user_id) DO NOTHING;",
        (user_id, username)
    )
    conn.commit()
    cur.close()
    conn.close()

    await message.answer("Привіт 👋! Тебе збережено у базі!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

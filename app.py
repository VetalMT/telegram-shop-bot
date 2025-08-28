import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from dotenv import load_dotenv

# Завантаження .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Логування
logging.basicConfig(level=logging.INFO)

# Ініціалізація бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =======================
# Клавіатури
# =======================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📦 Каталог"),
            KeyboardButton(text="🛒 Корзина")
        ]
    ],
    resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✅ Підтвердити"),
            KeyboardButton(text="❌ Скасувати")
        ]
    ],
    resize_keyboard=True
)

# =======================
# Команди
# =======================

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"Привіт, {message.from_user.full_name}! Виберіть опцію нижче:",
        reply_markup=main_keyboard
    )

@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Це бот-магазин. Використовуйте кнопки для навігації.",
        reply_markup=main_keyboard
    )

# =======================
# Обробка кнопок
# =======================

@dp.message(lambda message: message.text == "📦 Каталог")
async def show_catalog(message: types.Message):
    # Приклад виводу каталогу
    await message.answer("Ось наш каталог товарів:", reply_markup=main_keyboard)

@dp.message(lambda message: message.text == "🛒 Корзина")
async def show_cart(message: types.Message):
    # Приклад виводу корзини
    await message.answer("Ваша корзина порожня.", reply_markup=main_keyboard)

@dp.message(lambda message: message.text == "✅ Підтвердити")
async def confirm_order(message: types.Message):
    await message.answer("Ваше замовлення підтверджено!", reply_markup=main_keyboard)

@dp.message(lambda message: message.text == "❌ Скасувати")
async def cancel_order(message: types.Message):
    await message.answer("Ваше замовлення скасовано.", reply_markup=main_keyboard)

# =======================
# Логування всіх повідомлень (для адміна)
# =======================

@dp.message()
async def log_all_messages(message: types.Message):
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"Отримано повідомлення від {message.from_user.full_name}: {message.text}")

# =======================
# Запуск бота
# =======================

async def main():
    try:
        logging.info("Бот стартує...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

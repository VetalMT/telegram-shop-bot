import asyncio
import logging
import os
import asyncpg
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

# =======================
# Завантаження змінних середовища
# =======================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# =======================
# Логування
# =======================
logging.basicConfig(level=logging.INFO)

# =======================
# Ініціалізація бота
# =======================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# =======================
# Клавіатури
# =======================
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Каталог"), KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Підтвердити"), KeyboardButton(text="❌ Скасувати")]
    ],
    resize_keyboard=True
)

# =======================
# Підключення до бази даних
# =======================
async def create_db_pool():
    return await asyncpg.create_pool(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
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
# Функції роботи з БД
# =======================
async def get_products(pool):
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, price FROM products")
        return rows

async def add_to_cart(pool, user_id, product_id):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO cart(user_id, product_id) VALUES($1, $2)", user_id, product_id
        )

async def get_cart(pool, user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT p.name, p.price FROM cart c JOIN products p ON c.product_id = p.id WHERE c.user_id = $1",
            user_id
        )
        return rows

async def clear_cart(pool, user_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM cart WHERE user_id = $1", user_id)

# =======================
# Обробка кнопок
# =======================
@dp.message(lambda message: message.text == "📦 Каталог")
async def show_catalog(message: types.Message):
    pool = await create_db_pool()
    products = await get_products(pool)
    if not products:
        await message.answer("Каталог порожній.", reply_markup=main_keyboard)
        return
    text = "Наші товари:\n\n"
    for prod in products:
        text += f"{prod['id']}. {prod['name']} — {prod['price']}₴\n"
    text += "\nЩоб додати товар у корзину, напишіть його ID."
    await message.answer(text, reply_markup=main_keyboard)
    await pool.close()

@dp.message(lambda message: message.text.isdigit())
async def add_product_by_id(message: types.Message):
    product_id = int(message.text)
    pool = await create_db_pool()
    await add_to_cart(pool, message.from_user.id, product_id)
    await message.answer("Товар додано у корзину ✅", reply_markup=main_keyboard)
    await pool.close()

@dp.message(lambda message: message.text == "🛒 Корзина")
async def show_cart_cmd(message: types.Message):
    pool = await create_db_pool()
    items = await get_cart(pool, message.from_user.id)
    if not items:
        await message.answer("Ваша корзина порожня.", reply_markup=main_keyboard)
    else:
        text = "Ваша корзина:\n\n"
        total = 0
        for item in items:
            text += f"{item['name']} — {item['price']}₴\n"
            total += item['price']
        text += f"\nРазом: {total}₴"
        await message.answer(text, reply_markup=confirm_keyboard)
    await pool.close()

@dp.message(lambda message: message.text == "✅ Підтвердити")
async def confirm_order(message: types.Message):
    pool = await create_db_pool()
    await clear_cart(pool, message.from_user.id)
    await message.answer("Ваше замовлення підтверджено! ✅", reply_markup=main_keyboard)
    await pool.close()

@dp.message(lambda message: message.text == "❌ Скасувати")
async def cancel_order(message: types.Message):
    pool = await create_db_pool()
    await clear_cart(pool, message.from_user.id)
    await message.answer("Ваше замовлення скасовано ❌", reply_markup=main_keyboard)
    await pool.close()

# =======================
# Логування всіх повідомлень для адміна
# =======================
@dp.message()
async def log_all_messages(message: types.Message):
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"Отримано повідомлення від {message.from_user.full_name}: {message.text}")

# =======================
# Запуск бота
# =======================
async def main():
    logging.info("Бот стартує...")
    await dp.start_polling(bot)
    await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())

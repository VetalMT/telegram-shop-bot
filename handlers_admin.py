from aiogram.types import Message
from keyboards import admin_main_keyboard
from db import get_session
from database import Product
from sqlalchemy.future import select

async def admin_start_handler(message: Message):
    await message.answer("Адмін панель:", reply_markup=admin_main_keyboard())

# Додати товар
async def add_product_handler(message: Message):
    await message.answer("Введіть назву товару:")
    # Тут можна додати FSM для кроків: назва → опис → ціна → фото

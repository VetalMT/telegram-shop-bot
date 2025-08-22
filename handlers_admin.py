from aiogram import Router, F
from aiogram.types import Message
from keyboards import admin_kb
from db import add_product, get_products, delete_product
from config import ADMIN_ID

admin_router = Router()

# Перевірка чи адмін
async def is_admin(message: Message):
    return message.from_user.id == ADMIN_ID

# Додати товар
@admin_router.message(F.text == "➕ Додати товар")
async def add_item(message: Message):
    if not await is_admin(message):
        await message.answer("❌ Ви не адмін")
        return
    await message.answer("Введіть назву товару:")
    # Далі можна робити FSM для введення назви, ціни, опису

# Видалити товар
@admin_router.message(F.text == "❌ Видалити товар")
async def remove_item(message: Message):
    if not await is_admin(message):
        await message.answer("❌ Ви не адмін")
        return
    products = get_products()
    if not products:
        await message.answer("📦 Товарів немає")
        return
    text = "Список товарів:\n"
    for p in products:
        text += f"{p[0]}. {p[1]} - {p[2]} грн\n"
    await message.answer(text + "\nВведіть ID товару для видалення:")

# Переглянути товари
@admin_router.message(F.text == "📦 Переглянути товари")
async def view_items(message: Message):
    if not await is_admin(message):
        await message.answer("❌ Ви не адмін")
        return
    products = get_products()
    if not products:
        await message.answer("📦 Товарів немає")
        return
    text = "Список товарів:\n"
    for p in products:
        text += f"{p[0]}. {p[1]} - {p[2]} грн\n"
    await message.answer(text)

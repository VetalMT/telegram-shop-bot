from aiogram import Router, F
from aiogram.types import Message
from keyboards import admin_kb
from db import add_product, get_products, delete_product

admin_router = Router()

@admin_router.message(F.text == "➕ Додати товар")
async def add_product_start(message: Message):
    await message.answer("Введи назву товару:")
    # тут можна додати FSM для опису і ціни

@admin_router.message(F.text == "❌ Видалити товар")
async def delete_product_handler(message: Message):
    products = await get_products()
    if not products:
        await message.answer("Список товарів порожній")
        return
    text = "Список товарів:\n"
    for p in products:
        text += f"{p['id']}: {p['name']} - {p['price']}₴\n"
    await message.answer(text + "\nВведи ID товару для видалення:")

@admin_router.message(F.text == "📦 Переглянути товари")
async def view_products(message: Message):
    products = await get_products()
    if not products:
        await message.answer("Список товарів порожній")
        return
    text = "Товари:\n"
    for p in products:
        text += f"{p['id']}: {p['name']} - {p['price']}₴\n"
    await message.answer(text)

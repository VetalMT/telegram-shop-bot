from aiogram import Router, F
from aiogram.types import Message
from keyboards import shop_kb
from db import get_products

shop_router = Router()

@shop_router.message(F.text == "🛍 Переглянути товари")
async def show_products(message: Message):
    products = await get_products()
    if not products:
        await message.answer("Товари відсутні 😢")
        return
    text = "Наші товари:\n"
    for p in products:
        text += f"{p['id']}: {p['name']} - {p['price']}₴\n"
    await message.answer(text)

@shop_router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    # поки що можна залишити пустим, пізніше додамо корзину
    await message.answer("Твоя корзина порожня 🛒")

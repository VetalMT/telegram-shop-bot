from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards import catalog_button
from db import fetch

user_router = Router()

@user_router.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Бот готовий!", reply_markup=catalog_button)

@user_router.callback_query(F.data == "show_catalog")
async def show_catalog(callback: CallbackQuery):
    products = await fetch("SELECT id, name, price FROM products")
    if not products:
        await callback.message.answer("Каталог порожній.")
        return
    msg = "\n".join([f"{p['id']}. {p['name']} - {p['price']} грн" for p in products])
    await callback.message.answer(f"Каталог:\n{msg}")

@user_router.callback_query(F.data == "show_cart")
async def show_cart(callback: CallbackQuery):
    # тут можна додати логику для кошика
    await callback.message.answer("Ваш кошик поки що порожній.")

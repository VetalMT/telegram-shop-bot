from aiogram import F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import user_main_keyboard
from db import get_session
from database import Product, CartItem
from sqlalchemy.future import select

async def start_handler(message: Message):
    await message.answer("Бот готовий!", reply_markup=user_main_keyboard())

async def catalog_handler(message: Message):
    async for session in get_session():
        result = await session.execute(select(Product))
        products = result.scalars().all()
        if not products:
            await message.answer("Каталог порожній.")
            return
        for p in products:
            await message.bot.send_photo(
                chat_id=message.chat.id,
                photo=p.photo,
                caption=f"{p.name}\n{p.description}\nЦіна: {p.price} грн"
            )

async def cart_handler(message: Message):
    async for session in get_session():
        result = await session.execute(select(CartItem).where(CartItem.user_id == message.from_user.id))
        items = result.scalars().all()
        if not items:
            await message.answer("Ваш кошик порожній.")
            return
        text = "Ваш кошик:\n"
        for item in items:
            text += f"{item.product.name} x{item.quantity} - {item.product.price} грн\n"
        await message.answer(text)

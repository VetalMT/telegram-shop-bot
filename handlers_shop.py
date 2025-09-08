from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

shop_router = Router(name="shop")

@shop_router.message(Command("shop"))
async def shop_start(message: Message):
    await message.answer("🛍️ Ласкаво просимо в магазин!")

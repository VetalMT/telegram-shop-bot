from aiogram import Router, types
from aiogram.filters import Command

shop_router = Router()

@shop_router.message(Command("shop"))
async def shop_start(message: types.Message):
    await message.answer("🛍️ Ласкаво просимо в магазин!")

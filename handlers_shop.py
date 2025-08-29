from aiogram import Router, types
from aiogram.filters import Command

shop_router = Router(name="shop")

@shop_router.message(Command("shop"))
async def shop_start(message: types.Message):
    await message.answer("🛍️ Ласкаво просимо в магазин!\nВикористовуйте кнопки нижче ⬇️")

from aiogram import Dispatcher, F
from aiogram.types import Message


# Приклад команди /shop
async def shop_start(message: Message):
    await message.answer("🛍️ Ласкаво просимо в магазин!")


# Реєстрація хендлерів магазину
def setup_shop_handlers(dp: Dispatcher):
    dp.message.register(shop_start, F.text == "/shop")

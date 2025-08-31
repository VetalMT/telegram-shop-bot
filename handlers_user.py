from aiogram import Router, types
from aiogram.filters import Command
from db import get_products

user_router = Router()

def register_user_handlers(dp):
    dp.include_router(user_router)


@user_router.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Вітаю! Це тестовий магазин. Використовуйте /menu щоб побачити товари.")


@user_router.message(Command("menu"))
async def menu_cmd(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("❌ Немає доступних товарів")
        return
    response = "🛒 Доступні товари:\n\n"
    for p in products:
        response += f"📦 {p.name}\n💰 {p.price} грн\n\n"
    await message.answer(response)

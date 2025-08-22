from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from keyboards import shop_kb
from db import get_products

user_router = Router()

# --- Старт ---
@user_router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("👋 Вітаю у нашому магазині!", reply_markup=shop_kb)

# --- Перегляд товарів ---
@user_router.message(F.text == "🛍 Каталог")
async def view_products(message: Message):
    products = await get_products()
    if not products:
        return await message.answer("📭 Поки що немає товарів.")

    text = "📦 Наші товари:\n\n"
    for p in products:
        text += f"🆔 {p[0]} | {p[1]} — {p[3]} грн\n"
    text += "\nЩоб замовити, напишіть адміну через /admin"
    await message.answer(text)

# --- Перегляд корзини ---
@user_router.message(F.text == "🛒 Кошик")
async def view_cart(message: Message):
    await message.answer("🛒 Ваша корзина ще не реалізована, щоб додавати товари, зверніться до адміна.")

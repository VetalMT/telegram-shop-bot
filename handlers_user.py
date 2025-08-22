from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import shop_kb
from db import get_products, get_cart, add_to_cart as db_add_to_cart, clear_cart as db_clear_cart

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
    text += "\nЩоб додати товар у корзину, введіть команду:\n`/add ID` (де ID — номер товару)"
    await message.answer(text, parse_mode="Markdown")

# --- Додати товар у корзину ---
@user_router.message(F.text.startswith("/add"))
async def add_to_cart(message: Message):
    try:
        product_id = int(message.text.split()[1])
    except:
        return await message.answer("❌ Використовуйте формат: `/add ID`", parse_mode="Markdown")

    user_id = message.from_user.id
    await db_add_to_cart(user_id, product_id)
    await message.answer(f"✅ Товар з ID {product_id} додано у корзину.")

# --- Перегляд корзини ---
@user_router.message(F.text == "🛒 Кошик")
async def view_cart(message: Message):
    user_id = message.from_user.id
    items = await get_cart(user_id)

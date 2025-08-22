from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import shop_kb
from db import get_products, add_to_cart, get_cart, clear_cart as db_clear_cart, create_order

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
    text += "\nЩоб додати товар у кошик, введіть команду:\n`/add ID` (де ID — номер товару)"
    await message.answer(text, parse_mode="Markdown")

# --- Додати товар у корзину ---
@user_router.message(F.text.startswith("/add"))
async def add_to_cart_cmd(message: Message):
    try:
        product_id = int(message.text.split()[1])
    except:
        return await message.answer("❌ Використовуйте формат: `/add ID`", parse_mode="Markdown")

    await add_to_cart(message.from_user.id, product_id)
    await message.answer(f"✅ Товар з ID {product_id} додано у корзину.")

# --- Перегляд корзини ---
@user_router.message(F.text == "🛒 Кошик")
async def view_cart_cmd(message: Message):
    user_id = message.from_user.id
    items = await get_cart(user_id)
    if not items:
        return await message.answer("🛒 Ваша корзина порожня.")

    text = "🛒 Ваша корзина:\n\n"
    total = 0
    for i in items:
        text += f"📦 {i['name']} — {i['price']} грн x{i['qty']}\n"
        total += i['price'] * i['qty']

    text += f"\n💰 Всього: {total} грн"
    text += "\n\nЩоб очистити корзину введіть `/clear`.\nЩоб оформити замовлення введіть `/order`."
    await message.answer(text)

# --- Очистка корзини ---
@user_router.message(F.text == "/clear")
async def clear_cart_cmd(message: Message):
    user_id = message.from_user.id
    await db_clear_cart(user_id)
    await message.answer("🗑 Корзина очищена.")

# --- Оформлення замовлення ---
@user_router.message(F.text == "/order")
async def make_order_cmd(message: Message):
    user_id = message.from_user.id
    items = await get_cart(user_id)
    if not items:
        return await message.answer("🛒 Корзина порожня.")

    text = "✅ Ваше замовлення:\n\n"
    total = 0
    for i in items:
        text += f"📦 {i['name']} — {i['price']} грн x{i['qty']}\n"
        total += i['price'] * i['qty']

    text += f"\n💰 Загальна сума: {total} грн"
    text += "\n\n🔔 Наш менеджер скоро звʼяжеться з вами для підтвердження замовлення."

    await create_order(user_id, "Не вказано", "Не вказано", "Не вказано")  # приклад, можна додати форму
    await db_clear_cart(user_id)
    await message.answer(text)

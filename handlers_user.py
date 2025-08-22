from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards import shop_kb
from db import get_products

user_router = Router()

# тимчасове збереження корзини (в памʼяті)
# {user_id: [product_id, product_id, ...]}
cart = {}


# --- Старт ---
@user_router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("👋 Вітаю у нашому магазині!", reply_markup=shop_kb)


# --- Перегляд товарів ---
@user_router.message(F.text == "🛍 Переглянути товари")
async def view_products(message: Message):
    products = get_products()
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
    cart.setdefault(user_id, []).append(product_id)
    await message.answer(f"✅ Товар з ID {product_id} додано у корзину.")


# --- Перегляд корзини ---
@user_router.message(F.text == "🛒 Корзина")
async def view_cart(message: Message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        return await message.answer("🛒 Ваша корзина порожня.")

    products = get_products()
    user_cart = cart[user_id]
    text = "🛒 Ваша корзина:\n\n"
    total = 0

    for pid in user_cart:
        for p in products:
            if p[0] == pid:
                text += f"📦 {p[1]} — {p[3]} грн\n"
                total += p[3]

    text += f"\n💰 Всього: {total} грн"
    text += "\n\nЩоб очистити корзину введіть `/clear`.\nЩоб оформити замовлення введіть `/order`."
    await message.answer(text)


# --- Очистка корзини ---
@user_router.message(F.text == "/clear")
async def clear_cart(message: Message):
    user_id = message.from_user.id
    cart[user_id] = []
    await message.answer("🗑 Корзина очищена.")


# --- Оформлення замовлення ---
@user_router.message(F.text == "/order")
async def make_order(message: Message):
    user_id = message.from_user.id
    if user_id not in cart or not cart[user_id]:
        return await message.answer("🛒 Корзина порожня.")

    products = get_products()
    user_cart = cart[user_id]
    text = "✅ Ваше замовлення:\n\n"
    total = 0

    for pid in user_cart:
        for p in products:
            if p[0] == pid:
                text += f"📦 {p[1]} — {p[3]} грн\n"
                total += p[3]

    text += f"\n💰 Загальна сума: {total} грн"
    text += "\n\n🔔 Наш менеджер скоро звʼяжеться з вами для підтвердження замовлення."

    # очищаємо корзину після замовлення
    cart[user_id] = []

    await message.answer(text)

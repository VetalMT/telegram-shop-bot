from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import get_products, add_to_cart, get_cart, clear_cart

user_router = Router()

def user_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Кошик", callback_data="cart")]
    ])
    return kb

@user_router.message(commands=["start"])
async def start(message: types.Message):
    await message.answer("Вітаю! Головне меню:", reply_markup=user_menu())

@user_router.callback_query(lambda c: c.data == "catalog")
async def catalog(callback: types.CallbackQuery):
    products = await get_products()
    if not products:
        await callback.message.answer("Каталог порожній")
        return
    for p in products:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ В кошик", callback_data=f"add_{p[0]}")]
        ])
        await callback.message.answer_photo(
            photo=p[4],
            caption=f"📦 {p[1]}\n💬 {p[2]}\n💲 {p[3]} грн",
            reply_markup=kb
        )

@user_router.callback_query(lambda c: c.data.startswith("add_"))
async def add(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await add_to_cart(callback.from_user.id, product_id)
    await callback.answer("✅ Додано до кошика")

@user_router.callback_query(lambda c: c.data == "cart")
async def cart(callback: types.CallbackQuery):
    items = await get_cart(callback.from_user.id)
    if not items:
        await callback.message.answer("🛒 Кошик порожній")
        return
    text = "🛒 Ваш кошик:\n"
    total = 0
    for name, price in items:
        text += f"- {name} — {price} грн\n"
        total += price
    text += f"\nРазом: {total} грн"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Очистити", callback_data="clear_cart")]
    ])
    await callback.message.answer(text, reply_markup=kb)

@user_router.callback_query(lambda c: c.data == "clear_cart")
async def clear(callback: types.CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.message.answer("🗑 Кошик очищено")
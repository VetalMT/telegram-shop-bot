from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db import get_products, add_to_cart, get_cart, create_order

user_router = Router()

# --- Головне меню користувача ---
def user_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🛒 Переглянути кошик", callback_data="view_cart"),
        InlineKeyboardButton("🛍 Переглянути товари", callback_data="view_products")
    )
    return kb

# --- Старт ---
@user_router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Вітаю! Головне меню:", reply_markup=user_menu())

# --- Перегляд товарів ---
@user_router.callback_query(F.data=="view_products")
async def view_products(callback: types.CallbackQuery):
    products = await get_products()
    for p in products:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Додати в кошик", callback_data=f"add_{p[0]}")]
        ])
        text = f"{p[1]}\n{p[2]}\nЦіна: {p[3]}"
        await callback.message.answer_photo(p[4], caption=text, reply_markup=kb)
    await callback.answer()

# --- Додавання в кошик ---
@user_router.callback_query(F.data.startswith("add_"))
async def add_to_cart_cb(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    await add_to_cart(callback.from_user.id, pid)
    await callback.answer("Товар додано в кошик ✅")

# --- Перегляд кошика ---
@user_router.callback_query(F.data=="view_cart")
async def view_cart(callback: types.CallbackQuery):
    items = await get_cart(callback.from_user.id)
    if not items:
        await callback.message.answer("Ваш кошик порожній 🛒")
        return
    text = ""
    for i in items:
        text += f"{i['name']} x{i['qty']} = {i['price']*i['qty']}\n"
    await callback.message.answer(f"Ваш кошик:\n{text}\nЩоб оформити замовлення, напишіть /order")
    await callback.answer()

# --- Створення замовлення ---
@user_router.message(Command("order"))
async def create_order_cmd(message: types.Message):
    # Простий приклад: фіктивні дані для оформлення
    order_id = await create_order(message.from_user.id, "Ім'я Прізвище", "0999999999", "Адреса")
    if order_id:
        await message.answer(f"Замовлення #{order_id} успішно створено ✅")
    else:
        await message.answer("Кошик порожній, замовлення не створено.")
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from db import get_products, add_to_cart, get_cart, remove_from_cart, create_order

user_router = Router()

def user_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Мій кошик", callback_data="cart")],
            [InlineKeyboardButton(text="🛍️ Переглянути товари", callback_data="products")]
        ]
    )
    return kb

@user_router.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Вітаю! Головне меню:", reply_markup=user_menu())

@user_router.callback_query(lambda c: c.data == "products")
async def show_products(callback: types.CallbackQuery):
    products = await get_products()
    if not products:
        await callback.message.edit_text("Поки немає товарів 😔")
        return

    kb = InlineKeyboardMarkup(row_width=1)
    for p in products:
        kb.add(
            InlineKeyboardButton(
                text=f"{p[1]} - {p[3]}₴",
                callback_data=f"product_{p[0]}"
            )
        )
    await callback.message.edit_text("Товари:", reply_markup=kb)

@user_router.callback_query(lambda c: c.data.startswith("product_"))
async def product_detail(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    products = await get_products()
    product = next((p for p in products if p[0] == product_id), None)
    if not product:
        await callback.answer("Товар не знайдено", show_alert=True)
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("Додати в кошик", callback_data=f"add_{product_id}")],
            [InlineKeyboardButton("Назад до товарів", callback_data="products")]
        ]
    )
    await callback.message.edit_text(
        f"{product[1]}\n\n{product[2]}\n\nЦіна: {product[3]}₴",
        reply_markup=kb
    )

@user_router.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart_cb(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await add_to_cart(callback.from_user.id, product_id)
    await callback.answer("Товар додано в кошик ✅")

@user_router.callback_query(lambda c: c.data == "cart")
async def show_cart(callback: types.CallbackQuery):
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("Кошик порожній 🛒")
        return

    text = "Ваш кошик:\n"
    kb = InlineKeyboardMarkup(row_width=1)
    for item in cart:
        text += f"{item['name']} x{item['qty']} - {item['price']}₴\n"
        kb.add(InlineKeyboardButton(f"❌ Видалити {item['name']}", callback_data=f"remove_{item['product_id']}"))
    kb.add(InlineKeyboardButton("Оформити замовлення", callback_data="checkout"))
    await callback.message.edit_text(text, reply_markup=kb)

@user_router.callback_query(lambda c: c.data.startswith("remove_"))
async def remove_from_cart_cb(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await remove_from_cart(callback.from_user.id, product_id)
    await callback.answer("Товар видалено 🗑️")
    await show_cart(callback)

@user_router.callback_query(lambda c: c.data == "checkout")
async def checkout(callback: types.CallbackQuery):
    await callback.message.answer("Для оформлення замовлення напишіть ваше ім’я, телефон та адресу у форматі:\nІм'я, Телефон, Адреса")
    await callback.message.delete()
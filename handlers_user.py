from aiogram import Router, types
from aiogram.filters import Command, Text
from db import get_products, add_to_cart, get_cart, remove_from_cart, create_order

user_router = Router()

# Перегляд продуктів
@user_router.message(Command("shop"))
async def show_products(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("❌ Продуктів немає")
        return
    for p in products:
        text = f"{p[1]}\n{p[2]}\n💰 {p[3]} грн"
        if p[4]:
            await message.answer_photo(p[4], caption=text, reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{p[0]}")
            ))
        else:
            await message.answer(text, reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("🛒 Додати в кошик", callback_data=f"add_{p[0]}")
            ))

# Кошик
@user_router.message(Command("cart"))
async def show_cart(message: types.Message):
    cart = await get_cart(message.from_user.id)
    if not cart:
        await message.answer("🛒 Кошик порожній")
        return
    text = "🛒 Ваш кошик:\n\n"
    for item in cart:
        text += f"{item['name']} x{item['qty']} - {item['price']} грн\n"
    await message.answer(text)

# Inline кнопки для додавання/видалення з кошика
@user_router.callback_query(lambda c: c.data and c.data.startswith("add_"))
async def add_to_cart_cb(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[-1])
    await add_to_cart(callback.from_user.id, product_id)
    await callback.answer("✅ Додано в кошик")

@user_router.callback_query(lambda c: c.data and c.data.startswith("remove_"))
async def remove_from_cart_cb(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[-1])
    await remove_from_cart(callback.from_user.id, product_id)
    await callback.answer("❌ Видалено з кошика")

# Замовлення
@user_router.message(Command("order"))
async def create_order_cmd(message: types.Message):
    order_id = await create_order(message.from_user.id, "Тест", "0000000000", "Адреса")
    if order_id:
        await message.answer(f"✅ Замовлення створено! Номер: {order_id}")
    else:
        await message.answer("❌ Ваш кошик порожній")
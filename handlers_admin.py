from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db import add_product, delete_product, get_products

admin_router = Router()
ADMIN_ID = 123456789  # замініть на свій Telegram ID

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Немає доступу")
        return
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("Додати товар", callback_data="add_product"))
    kb.add(InlineKeyboardButton("Переглянути товари", callback_data="list_products"))
    await message.answer("Панель адміністратора:", reply_markup=kb)

@admin_router.callback_query(lambda c: c.data == "add_product")
async def add_product_cb(callback: types.CallbackQuery):
    await callback.message.answer("Надішліть дані товару у форматі:\nНазва, Опис, Ціна, photo_id")
    await callback.message.delete()

@admin_router.message()
async def add_product_message(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    try:
        name, description, price, photo_id = message.text.split(",", 3)
        price = float(price.strip())
        product_id = await add_product(name.strip(), description.strip(), price, photo_id.strip())
        await message.answer(f"Товар додано ✅ (ID: {product_id})")
    except Exception as e:
        await message.answer(f"Помилка при додаванні: {e}")

@admin_router.callback_query(lambda c: c.data == "list_products")
async def list_products_cb(callback: types.CallbackQuery):
    products = await get_products()
    if not products:
        await callback.message.edit_text("Товарів немає")
        return
    kb = InlineKeyboardMarkup(row_width=1)
    for p in products:
        kb.add(InlineKeyboardButton(f"❌ Видалити {p[1]}", callback_data=f"delete_{p[0]}"))
    await callback.message.edit_text("Список товарів:", reply_markup=kb)

@admin_router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_product_cb(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await delete_product(product_id)
    await callback.answer("Товар видалено ✅")
    await list_products_cb(callback)
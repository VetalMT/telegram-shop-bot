from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
import aiosqlite

shop_router = Router()

# Меню
@shop_router.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="🛒 Кошик", callback_data="cart")]
    ])
    await message.answer("Вітаю у магазині! Обери дію:", reply_markup=kb)

# Каталог
@shop_router.callback_query(F.data == "catalog")
async def show_catalog(callback: CallbackQuery):
    async with aiosqlite.connect("shop.db") as db:
        async with db.execute("SELECT id, name, description, price, photo FROM products") as cursor:
            rows = await cursor.fetchall()
    if not rows:
        await callback.message.answer("Каталог пустий.")
        return
    for row in rows:
        product_id, name, desc, price, photo = row
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Додати в кошик", callback_data=f"add_{product_id}")]
        ])
        if photo:
            await callback.message.answer_photo(photo=photo,
                                                caption=f"📦 {name}\n💰 {price} грн\n\n{desc}",
                                                reply_markup=kb)
        else:
            await callback.message.answer(f"📦 {name}\n💰 {price} грн\n\n{desc}",
                                          reply_markup=kb)

# Додавання в кошик
@shop_router.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    async with aiosqlite.connect("shop.db") as db:
        await db.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)", (user_id, product_id))
        await db.commit()
    await callback.answer("✅ Додано в кошик!")

# Перегляд кошика
@shop_router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    async with aiosqlite.connect("shop.db") as db:
        async with db.execute("""
            SELECT p.name, p.price, c.quantity 
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = ?
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
    if not rows:
        await callback.message.answer("🛒 Кошик пустий.")
        return
    text = "🛒 Ваш кошик:\n\n"
    total = 0
    for name, price, qty in rows:
        total += price * qty
        text += f"{name} x{qty} = {price*qty} грн\n"
    text += f"\n💰 Всього: {total} грн"
    await callback.message.answer(text)

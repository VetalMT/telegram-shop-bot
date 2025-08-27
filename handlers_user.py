from aiogram import Router, types
from aiogram.filters import Command
from db import fetch_categories, fetch_products

user_router = Router()


@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Привіт! Виберіть категорію:", reply_markup=await categories_keyboard())


async def categories_keyboard():
    categories = await fetch_categories()
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat_id, name in categories:
        kb.add(types.KeyboardButton(text=f"{name} ({cat_id})"))
    return kb


@user_router.message()
async def show_products(message: types.Message):
    try:
        # формат: НазваКатегорії (id)
        cat_id = int(message.text.split("(")[-1].strip(")"))
        products = await fetch_products(cat_id)
        if not products:
            return await message.answer("❌ У цій категорії немає товарів")
        text = "📦 Товари:\n"
        for prod_id, name, price in products:
            text += f"• {name} — {price} грн\n"
        await message.answer(text)
    except Exception:
        await message.answer("❓ Не зрозумів... Виберіть категорію з меню")
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from db import add_product, delete_product, get_products

admin_router = Router()

ADMIN_ID = 123456789  # <- заміни на свій Telegram ID

# --- Кнопки ---
def admin_main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("Додати товар", callback_data="admin_add"),
        InlineKeyboardButton("Переглянути товари", callback_data="admin_list"),
    )
    return kb

# --- Хендлери ---
@admin_router.message(Command("admin"))
async def admin_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Головне меню адміністратора:", reply_markup=admin_main_menu())

# --- Додавання товару ---
@admin_router.callback_query(F.data=="admin_add")
async def admin_add_product_start(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return
    await callback.message.answer("Введіть назву товару:")
    await callback.message.bot.set_state(callback.from_user.id, "adding_name")
    await callback.answer()

@admin_router.message(F.state=="adding_name")
async def admin_add_name(message: types.Message):
    message.bot_data = {"name": message.text}
    await message.answer("Введіть опис товару:")
    await message.bot.set_state(message.from_user.id, "adding_description")

@admin_router.message(F.state=="adding_description")
async def admin_add_description(message: types.Message):
    message.bot_data["description"] = message.text
    await message.answer("Введіть ціну товару:")
    await message.bot.set_state(message.from_user.id, "adding_price")

@admin_router.message(F.state=="adding_price")
async def admin_add_price(message: types.Message):
    try:
        price = float(message.text)
    except:
        await message.answer("Ціна повинна бути числом. Спробуйте ще раз:")
        return
    message.bot_data["price"] = price
    await message.answer("Надішліть фото товару:")
    await message.bot.set_state(message.from_user.id, "adding_photo")

@admin_router.message(F.content_type=="photo", F.state=="adding_photo")
async def admin_add_photo(message: types.Message):
    photo_id = message.photo[-1].file_id
    data = message.bot_data
    await add_product(data["name"], data["description"], data["price"], photo_id)
    await message.answer("Товар додано ✅", reply_markup=admin_main_menu())
    await message.bot.set_state(message.from_user.id, None)

# --- Перегляд і видалення товарів ---
@admin_router.callback_query(F.data=="admin_list")
async def admin_list_products(callback: types.CallbackQuery):
    products = await get_products()
    if not products:
        await callback.message.answer("Список товарів порожній.")
        return
    for p in products:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Видалити", callback_data=f"del_{p[0]}")]
        ])
        text = f"ID: {p[0]}\nНазва: {p[1]}\nОпис: {p[2]}\nЦіна: {p[3]}"
        await callback.message.answer_photo(p[4], caption=text, reply_markup=kb)
    await callback.answer()

@admin_router.callback_query(F.data.startswith("del_"))
async def admin_delete_product(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    await delete_product(pid)
    await callback.message.answer("Товар видалено ✅")
    await callback.answer()
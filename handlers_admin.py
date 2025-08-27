from aiogram import Router, types, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from db import add_product, delete_product, get_products

admin_router = Router()

class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()

@admin_router.message(commands=["admin"])
async def admin_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Додати товар", callback_data="add_product")],
        [InlineKeyboardButton(text="🗑 Видалити товар", callback_data="del_product")],
        [InlineKeyboardButton(text="📦 Список товарів", callback_data="list_products")]
    ])
    await message.answer("Адмін-панель:", reply_markup=kb)

# Додавання товару
@admin_router.callback_query(F.data == "add_product")
async def add_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return
    await state.set_state(AddProductFSM.name)
    await callback.message.answer("Введи назву товару:")

@admin_router.message(AddProductFSM.name)
async def add_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProductFSM.description)
    await message.answer("Введи опис товару:")

@admin_router.message(AddProductFSM.description)
async def add_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProductFSM.price)
    await message.answer("Введи ціну:")

@admin_router.message(AddProductFSM.price)
async def add_price(message: types.Message, state: FSMContext):
    await state.update_data(price=float(message.text))
    await state.set_state(AddProductFSM.photo)
    await message.answer("Надішли фото:")

@admin_router.message(AddProductFSM.photo, F.photo)
async def add_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_product(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        photo_id=message.photo[-1].file_id
    )
    await state.clear()
    await message.answer("✅ Товар додано")

# Видалення товару
@admin_router.callback_query(F.data == "del_product")
async def delete_menu(callback: types.CallbackQuery):
    products = await get_products()
    if not products:
        await callback.message.answer("❌ Немає товарів")
        return
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=f"❌ {p[1]}", callback_data=f"delete_{p[0]}")] for p in products]
    )
    await callback.message.answer("Вибери товар для видалення:", reply_markup=kb)

@admin_router.callback_query(lambda c: c.data.startswith("delete_"))
async def delete_item(callback: types.CallbackQuery):
    pid = int(callback.data.split("_")[1])
    await delete_product(pid)
    await callback.message.answer("🗑 Товар видалено")

# Перегляд списку
@admin_router.callback_query(F.data == "list_products")
async def list_products(callback: types.CallbackQuery):
    products = await get_products()
    if not products:
        await callback.message.answer("❌ Каталог порожній")
        return
    text = "📦 Товари:\n"
    for p in products:
        text += f"{p[0]}. {p[1]} — {p[3]} грн\n"
    await callback.message.answer(text)
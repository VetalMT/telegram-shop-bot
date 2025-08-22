from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from keyboards import admin_kb
from db import add_product, get_products, delete_product
from states import AddProduct

admin_router = Router()


# --- Вхід в адмінку ---
@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return await message.answer("⛔ У вас немає доступу до адмін-панелі")
    await message.answer("⚙️ Адмін панель", reply_markup=admin_kb)


# --- Додавання товару ---
@admin_router.message(F.text == "➕ Додати товар")
async def add_product_start(message: Message, state: FSMContext):
    await state.set_state(AddProduct.name)
    await message.answer("Введіть назву товару:")


@admin_router.message(AddProduct.name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer("Введіть опис товару:")


@admin_router.message(AddProduct.description)
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer("Введіть ціну товару (число):")


@admin_router.message(AddProduct.price)
async def add_product_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        return await message.answer("❌ Ціна має бути числом. Введіть ще раз:")

    await state.update_data(price=price)
    await state.set_state(AddProduct.photo)
    await message.answer("Надішліть фото товару:")


@admin_router.message(AddProduct.photo, F.photo)
async def add_product_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id

    # запис у базу
    add_product(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        photo=photo_id
    )

    await state.clear()
    await message.answer("✅ Товар успішно доданий!", reply_markup=admin_kb)


# --- Перегляд товарів ---
@admin_router.message(F.text == "📦 Переглянути товари")
async def view_products(message: Message):
    products = get_products()
    if not products:
        return await message.answer("📭 У базі немає товарів.")

    for p in products:
        await message.answer_photo(
            photo=p[4],
            caption=f"🆔 {p[0]}\n📦 {p[1]}\n💬 {p[2]}\n💲 {p[3]}"
        )


# --- Видалення товару ---
@admin_router.message(F.text == "❌ Видалити товар")
async def delete_product_start(message: Message):
    products = get_products()
    if not products:
        return await message.answer("📭 У базі немає товарів.")

    text = "Введіть ID товару, який хочете видалити:\n\n"
    for p in products:
        text += f"🆔 {p[0]} | {p[1]} — {p[3]} грн\n"
    await message.answer(text)


@admin_router.message()
async def delete_product_by_id(message: Message):
    if message.text.isdigit():
        product_id = int(message.text)
        delete_product(product_id)
        await message.answer(f"✅ Товар з ID {product_id} видалено.", reply_markup=admin_kb)

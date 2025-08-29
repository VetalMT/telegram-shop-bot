from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from keyboards import admin_keyboard
from db import execute, fetch
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

admin_router = Router()

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()

class DeleteProduct(StatesGroup):
    id = State()

@admin_router.message(F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer("Панель адміністратора:", reply_markup=admin_keyboard)

@admin_router.callback_query(F.data == "add_product")
async def add_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddProduct.name)
    await callback.message.answer("Введіть назву товару:")

@admin_router.message(AddProduct.name)
async def product_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer("Введіть опис товару:")

@admin_router.message(AddProduct.description)
async def product_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer("Введіть ціну товару:")

@admin_router.message(AddProduct.price)
async def product_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AddProduct.photo)
    await message.answer("Надішліть фото товару:")

@admin_router.message(AddProduct.photo, F.photo)
async def product_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    await execute(
        "INSERT INTO products (name, description, price, photo_id) VALUES ($1,$2,$3,$4)",
        data['name'], data['description'], data['price'], photo_id
    )
    await message.answer("Товар додано!")
    await state.clear()

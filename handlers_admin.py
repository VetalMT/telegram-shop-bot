from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from keyboards import admin_kb
from db import add_product

admin_router = Router()


# --- СТАНИ ДЛЯ FSM ---
class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()


# --- Перевірка що це адмін ---
def is_admin(message: Message) -> bool:
    return str(message.from_user.id) == str(ADMIN_ID)


# --- Вхід в адмінку ---
@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message):
        await message.answer("⛔ У тебе немає прав доступу!")
        return
    await message.answer("⚙️ Адмін панель", reply_markup=admin_kb)


# --- Додавання товару ---
@admin_router.message(F.text == "➕ Додати товар")
async def start_add_product(message: Message, state: FSMContext):
    if not is_admin(message):
        return
    await state.set_state(AddProduct.name)
    await message.answer("Введи назву товару:", reply_markup=ReplyKeyboardRemove())


@admin_router.message(AddProduct.name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer("Тепер введи опис товару:")


@admin_router.message(AddProduct.description)
async def add_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.price)
    await message.answer("Введи ціну товару (наприклад: 199.99):")


@admin_router.message(AddProduct.price)
async def add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("❌ Невірний формат. Введи число.")
        return

    await state.update_data(price=price)
    await state.set_state(AddProduct.photo)
    await message.answer("Надішли фото товару (або пропусти, відправивши - )")


@admin_router.message(AddProduct.photo)
async def add_photo(message: Message, state: FSMContext):
    data = await state.get_data()

    name = data["name"]
    description = data["description"]
    price = data["price"]

    # Якщо фото відправлене
    if message.photo:
        photo = message.photo[-1].file_id
    elif message.text == "-":
        photo = None
    else:
        await message.answer("Надішли фото або '-' для пропуску")
        return

    # Зберігаємо в базу
    add_product(name, description, price, photo)

    await message.answer(
        f"✅ Товар додано!\n\n"
        f"📦 {name}\n"
        f"💰 {price} грн\n"
        f"📝 {description}",
        reply_markup=admin_kb
    )
    await state.clear()

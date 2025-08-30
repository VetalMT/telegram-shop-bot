from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
import db

router = Router()


class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()


@router.message(Command("admin"))
async def admin_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ У вас немає доступу")

    keyboard = [
        [types.KeyboardButton(text="➕ Додати товар")],
        [types.KeyboardButton(text="❌ Видалити товар")],
        [types.KeyboardButton(text="📦 Список товарів")],
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer("Адмін-панель:", reply_markup=markup)


# ================== ADD PRODUCT ==================
@router.message(lambda m: m.text == "➕ Додати товар")
async def add_product_start(message: types.Message, state: FSMContext):
    await state.set_state(AddProductFSM.name)
    await message.answer("Введіть назву товару:")


@router.message(AddProductFSM.name)
async def add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProductFSM.description)
    await message.answer("Введіть опис товару:")


@router.message(AddProductFSM.description)
async def add_product_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProductFSM.price)
    await message.answer("Введіть ціну товару:")


@router.message(AddProductFSM.price)
async def add_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        return await message.answer("❌ Введіть число")
    await state.update_data(price=price)
    await state.set_state(AddProductFSM.photo)
    await message.answer("Надішліть фото товару:")


@router.message(AddProductFSM.photo)
async def add_product_photo(message: types.Message, state: FSMContext, pool):
    if not message.photo:
        return await message.answer("Надішліть саме фото!")
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    await db.add_product(pool, data["name"], data["description"], data["price"], file_id)
    await state.clear()
    await message.answer("✅ Товар додано!")


# ================== DELETE PRODUCT ==================
@router.message(lambda m: m.text == "❌ Видалити товар")
async def delete_product_start(message: types.Message, pool):
    products = await db.get_products(pool)
    if not products:
        return await message.answer("Немає товарів")
    text = "Список товарів:\n"
    for p in products:
        text += f"{p['id']}. {p['name']} - {p['price']} грн\n"
    text += "\nВведіть ID товару для видалення:"
    await message.answer(text)


@router.message(lambda m: m.text.isdigit())
async def delete_product(message: types.Message, pool):
    await db.delete_product(pool, int(message.text))
    await message.answer("✅ Товар видалено")


# ================== LIST PRODUCTS ==================
@router.message(lambda m: m.text == "📦 Список товарів")
async def list_products(message: types.Message, pool):
    products = await db.get_products(pool)
    if not products:
        return await message.answer("Немає товарів")
    text = "Список товарів:\n"
    for p in products:
        text += f"{p['id']}. {p['name']} - {p['price']} грн\n"
    await message.answer(text)

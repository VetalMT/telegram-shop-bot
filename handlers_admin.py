from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db import add_product, delete_product, get_products
from config import ADMINS

admin_router = Router()

# ---------- FSM для додавання продукту ----------
class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()

# Перевірка на admin
def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

# Старт адмін меню
@admin_router.message(Command("admin"))
async def admin_start(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("🚫 Ти не адмін")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("Додати продукт", "Видалити продукт")
    await message.answer("👑 Адмін панель", reply_markup=kb)

# Додати продукт
@admin_router.message(Text("Додати продукт"))
async def admin_add_product(message: types.Message, state: FSMContext):
    await message.answer("Введи назву продукту:")
    await state.set_state(AddProduct.name)

@admin_router.message(AddProduct.name)
async def admin_add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введи опис продукту:")
    await state.set_state(AddProduct.description)

@admin_router.message(AddProduct.description)
async def admin_add_product_desc(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введи ціну продукту:")
    await state.set_state(AddProduct.price)

@admin_router.message(AddProduct.price)
async def admin_add_product_price(message: types.Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        await message.answer("Введи правильну ціну (число).")
        return
    await state.update_data(price=price)
    await message.answer("Надішли фото продукту або /skip")
    await state.set_state(AddProduct.photo)

@admin_router.message(AddProduct.photo, content_types=types.ContentType.PHOTO)
async def admin_add_product_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    await add_product(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        photo_id=photo_id
    )
    await message.answer("✅ Продукт додано!")
    await state.clear()

@admin_router.message(AddProduct.photo, commands="skip")
async def admin_add_product_skip_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await add_product(
        name=data["name"],
        description=data["description"],
        price=data["price"],
        photo_id=None
    )
    await message.answer("✅ Продукт додано без фото!")
    await state.clear()

# Видалити продукт
@admin_router.message(Text("Видалити продукт"))
async def admin_delete_product(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("Продуктів немає.")
        return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for p in products:
        kb.add(types.KeyboardButton(f"{p[1]} | ID:{p[0]}"))
    kb.add("Відмінити")
    await message.answer("Вибери продукт для видалення:", reply_markup=kb)

@admin_router.message()
async def admin_delete_product_select(message: types.Message):
    if message.text == "Відмінити":
        await message.answer("❌ Відмінено", reply_markup=types.ReplyKeyboardRemove())
        return
    if "ID:" not in message.text:
        await message.answer("Невірний формат")
        return
    try:
        product_id = int(message.text.split("ID:")[-1])
    except ValueError:
        await message.answer("Невірний формат ID")
        return
    from db import delete_product
    deleted = await delete_product(product_id)
    if deleted:
        await message.answer("✅ Продукт видалено", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("❌ Не вдалося видалити", reply_markup=types.ReplyKeyboardRemove())
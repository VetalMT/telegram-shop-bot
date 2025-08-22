from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import ADMIN_ID, products

router = Router()

class AddProduct(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()

# --- Додати товар ---
@router.message(Command("add"))
async def admin_add(message: Message, state: FSMContext):
    if str(message.from_user.id) != ADMIN_ID:
        return await message.answer("⛔ Доступ заборонено.")
    await state.set_state(AddProduct.waiting_for_name)
    await message.answer("Введіть назву товару:")

@router.message(AddProduct.waiting_for_name)
async def add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.waiting_for_description)
    await message.answer("Введіть опис товару:")

@router.message(AddProduct.waiting_for_description)
async def add_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddProduct.waiting_for_price)
    await message.answer("Введіть ціну товару:")

@router.message(AddProduct.waiting_for_price)
async def add_price(message: Message, state: FSMContext):
    try:
        price = float(message.text)
    except ValueError:
        return await message.answer("❌ Введіть коректну ціну (число).")
    await state.update_data(price=price)
    await state.set_state(AddProduct.waiting_for_photo)
    await message.answer("Надішліть фото товару:")

@router.message(AddProduct.waiting_for_photo, F.photo)
async def add_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    products.append({
        "id": len(products) + 1,
        "name": data["name"],
        "description": data["description"],
        "price": data["price"],
        "photo": message.photo[-1].file_id  # ✅ зберігаємо file_id фото
    })
    await state.clear()
    await message.answer("✅ Товар додано!")

# --- Переглянути товари ---
@router.message(Command("list"))
async def admin_list(message: Message):
    if str(message.from_user.id) != ADMIN_ID:
        return await message.answer("⛔ Доступ заборонено.")
    if not products:
        return await message.answer("📭 Немає товарів.")
    for p in products:
        kb = InlineKeyboardBuilder()
        kb.button(text="❌ Видалити", callback_data=f"delete:{p['id']}")
        kb.adjust(1)
        await message.answer_photo(
            photo=p["photo"],
            caption=f"<b>{p['name']}</b>\n{p['description']}\n💰 {p['price']} грн",
            reply_markup=kb.as_markup()
        )

# --- Видалити товар ---
@router.callback_query(F.data.startswith("delete:"))
async def admin_delete_cb(cb: CallbackQuery):
    product_id = int(cb.data.split(":")[1])
    global products
    products = [p for p in products if p["id"] != product_id]
    try:
        await cb.message.edit_caption("🗑 Товар видалено.")
    except:
        await cb.message.answer("🗑 Товар видалено.")
    await cb.answer()

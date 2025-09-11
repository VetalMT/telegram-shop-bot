from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from keyboards import admin_kb
from db import add_product, get_products, delete_product, count_products

admin_router = Router(name="admin")

# ---------- FSM для додавання товару ----------
class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()
    confirm = State()

# /admin меню
@admin_router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас немає прав адміністратора.")
        return
    await message.answer("⚙️ Адмін-панель. Оберіть дію:", reply_markup=admin_kb)

# Старт додавання товару
@admin_router.message(F.text == "➕ Додати товар")
async def admin_add_product_start(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.set_state(AddProductFSM.name)
    await message.answer("📝 Введіть назву товару:")

@admin_router.message(AddProductFSM.name)
async def admin_add_product_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddProductFSM.description)
    await message.answer("✍️ Введіть опис товару:")

@admin_router.message(AddProductFSM.description)
async def admin_add_product_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddProductFSM.price)
    await message.answer("💵 Введіть ціну (число, напр. 199.99):")

@admin_router.message(AddProductFSM.price)
async def admin_add_product_price(message: types.Message, state: FSMContext):
    text = message.text.replace(",", ".").strip()
    try:
        price = float(text)
    except ValueError:
        await message.answer("❗ Невірний формат. Введіть число, напр. 199.99")
        return
    await state.update_data(price=price)
    await state.set_state(AddProductFSM.photo)
    await message.answer("📸 Надішліть фото товару або введіть /skip щоб пропустити.")

@admin_router.message(Command("skip"), AddProductFSM.photo)
async def admin_add_product_skip_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo_id=None)
    await _confirm_product(message, state)

@admin_router.message(AddProductFSM.photo, F.photo)
async def admin_add_product_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await _confirm_product(message, state)

async def _confirm_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = (
        "Підтвердіть товар:\n"
        f"• Назва: {data.get('name')}\n"
        f"• Опис: {data.get('description')}\n"
        f"• Ціна: {data.get('price')}\n"
        f"• Фото: {'є' if data.get('photo_id') else 'немає'}\n\n"
        "Надішліть '+' щоб зберегти або '-' щоб скасувати."
    )
    await state.set_state(AddProductFSM.confirm)
    await message.answer(text)

@admin_router.message(AddProductFSM.confirm, F.text.in_({"+", "-"}))
async def admin_add_product_confirm(message: types.Message, state: FSMContext):
    txt = message.text.strip()
    if txt == "-":
        await state.clear()
        await message.answer("❌ Додавання скасовано.", reply_markup=admin_kb)
        return
    data = await state.get_data()
    await add_product(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
        photo_id=data.get("photo_id"),
    )
    await state.clear()
    await message.answer("✅ Товар додано!", reply_markup=admin_kb)

# Перегляд товарів (списком з ID)
@admin_router.message(F.text == "📦 Переглянути товари")
async def admin_view_products(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    products = await get_products(limit=50, offset=0)
    if not products:
        await message.answer("📭 У каталозі поки немає товарів.")
        return
    lines = []
    for pid, name, desc, price, photo_id in products:
        lines.append(f"#{pid} — {name} | {price} грн")
    await message.answer("📋 Список товарів:\n" + "\n".join(lines))

# Видалення товару - запит ID
@admin_router.message(F.text == "❌ Видалити товар")
async def admin_delete_prompt(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    total = await count_products()
    await message.answer(
        f"Введіть ID товару для видалення. Усього товарів: {total}\nПриклад: 12"
    )

@admin_router.message(F.text.regexp(r"^\d+$"))
async def admin_delete_by_id(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    pid = int(message.text)
    ok = await delete_product(pid)
    if ok:
        await message.answer(f"✅ Товар #{pid} видалено.")
    else:
        await message.answer(f"❗ Товар #{pid} не знайдено.")

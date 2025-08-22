from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from config import ADMIN_ID
from keyboards import admin_kb, delete_product_kb
from db import add_product, get_products, delete_product, count_products

admin_router = Router()

class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()

@admin_router.message(Command("admin"))
async def admin_panel(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return await msg.answer("⛔️ Доступ тільки для адміністратора.")
    await msg.answer("Адмін-панель:", reply_markup=admin_kb)

# ---- ДОДАТИ ТОВАР ----
@admin_router.message(F.text == "➕ Додати товар")
async def add_start(msg: Message, state: FSMContext):
    if msg.from_user.id != ADMIN_ID:
        return
    await state.set_state(AddProductFSM.name)
    await msg.answer("Введіть назву товару:")

@admin_router.message(AddProductFSM.name)
async def add_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await state.set_state(AddProductFSM.description)
    await msg.answer("Опишіть товар:")

@admin_router.message(AddProductFSM.description)
async def add_desc(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text.strip())
    await state.set_state(AddProductFSM.price)
    await msg.answer("Вкажіть ціну (число):")

@admin_router.message(AddProductFSM.price)
async def add_price(msg: Message, state: FSMContext):
    try:
        price = float(msg.text.replace(",", "."))
    except Exception:
        return await msg.answer("❗️ Невірний формат. Вкажіть число, напр. 199.99")
    await state.update_data(price=price)
    await state.set_state(AddProductFSM.photo)
    await msg.answer("Надішліть фото товару (можна пропустити командою /skip).")

@admin_router.message(Command("skip"), AddProductFSM.photo)
async def skip_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    product_id = await add_product(
        data["name"], data["description"], data["price"], photo_id=None
    )
    await state.clear()
    await msg.answer(f"✅ Товар #{product_id} додано без фото.")

@admin_router.message(AddProductFSM.photo, F.photo)
async def add_photo(msg: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = msg.photo[-1].file_id
    product_id = await add_product(
        data["name"], data["description"], data["price"], photo_id=photo_id
    )
    await state.clear()
    await msg.answer(f"✅ Товар #{product_id} додано.")

# ---- ПЕРЕГЛЯД/ВИДАЛЕННЯ ----
@admin_router.message(F.text == "📦 Переглянути товари")
async def admin_view_products(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    items = await get_products(limit=20, offset=0)
    if not items:
        return await msg.answer("Список товарів порожній.")
    for pid, name, description, price, photo_id in items:
        text = f"#{pid} • <b>{name}</b>\n{description}\nЦіна: {price:.2f} ₴"
        if photo_id:
            await msg.bot.send_photo(msg.chat.id, photo=photo_id, caption=text, parse_mode="HTML",
                                     reply_markup=delete_product_kb(pid))
        else:
            await msg.answer(text, parse_mode="HTML", reply_markup=delete_product_kb(pid))

@admin_router.message(F.text == "❌ Видалити товар")
async def delete_hint(msg: Message):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer("Натисніть «🗑 Видалити» під потрібним товаром у списку «📦 Переглянути товари».")

@admin_router.callback_query(F.data.startswith("adm_del:"))
async def admin_delete_cb(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return await cb.answer("Нема доступу", show_alert=True)
    pid = int(cb.data.split(":")[1])
    ok = await delete_product(pid)
    if ok:
        await cb.message.edit_text("🗑 Товар видалено.")
    else:
        await cb.answer("Не знайдено", show_alert=True)

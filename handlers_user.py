from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import shop_kb, product_inline_kb, cart_inline_kb
from db import get_products, add_to_cart, get_cart, clear_cart, create_order

user_router = Router()

# ====== FSM для оформлення замовлення ======
class OrderForm(StatesGroup):
    full_name = State()
    phone = State()
    address = State()

# ====== Допоміжне: показ кошика ======
async def send_cart(message: Message):
    items = await get_cart(message.from_user.id)
    if not items:
        return await message.answer("🛒 Ваша корзина порожня.")
    text = "🛒 Ваша корзина:\n\n"
    total = 0.0
    for it in items:
        line = f"• {it['name']} × {it['qty']} — {it['price']*it['qty']} грн\n"
        text += line
        total += it["price"] * it["qty"]
    text += f"\n💰 Всього: {total} грн"
    await message.answer(text, reply_markup=cart_inline_kb())

# ====== Старт ======
@user_router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("👋 Вітаю у нашому магазині!", reply_markup=shop_kb)

# ====== Каталог ======
@user_router.message(F.text == "🛍 Каталог")
async def view_products(message: Message):
    products = await get_products()
    if not products:
        return await message.answer("📭 Поки що немає товарів.")

    await message.answer("📦 Наші товари:")
    for pid, name, desc, price, photo_id in products:
        caption = f"🆔 {pid}\n{name}\n{desc}\n💸 {price} грн"
        if photo_id:
            await message.answer_photo(photo_id, caption=caption, reply_markup=product_inline_kb(pid))
        else:
            await message.answer(caption, reply_markup=product_inline_kb(pid))

# ====== Кошик (кнопка) ======
@user_router.message(F.text == "🛒 Кошик")
async def open_cart_btn(message: Message):
    await send_cart(message)

# ====== Callback: додати у кошик ======
@user_router.callback_query(F.data.startswith("add:"))
async def cb_add_to_cart(callback: CallbackQuery):
    product_id = int(callback.data.split(":")[1])
    await add_to_cart(callback.from_user.id, product_id, 1)
    await callback.answer("✅ Додано до кошика")
    await callback.message.edit_reply_markup(reply_markup=product_inline_kb(product_id))

# ====== Callback: відкрити кошик ======
@user_router.callback_query(F.data == "cart:open")
async def cb_cart_open(callback: CallbackQuery):
    await callback.answer()
    await send_cart(callback.message)

# ====== Callback: очистити кошик ======
@user_router.callback_query(F.data == "cart:clear")
async def cb_cart_clear(callback: CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.answer("🧹 Кошик очищено")
    await callback.message.edit_text("🛒 Ваша корзина порожня.")

# ====== Callback: оформити замовлення (почати FSM) ======
@user_router.callback_query(F.data == "order:start")
async def cb_order_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(OrderForm.full_name)
    await callback.message.answer("✍️ Вкажіть Ваше ПІБ (Прізвище Ім'я По батькові):")

@user_router.message(OrderForm.full_name)
async def ask_phone(message: Message, state: FSMContext):
    full_name = message.text.strip()
    if len(full_name) < 4:
        return await message.answer("Будь ласка, введіть коректне ПІБ.")
    await state.update_data(full_name=full_name)
    await state.set_state(OrderForm.phone)
    await message.answer("📞 Вкажіть Ваш номер телефону:")

@user_router.message(OrderForm.phone)
async def ask_address(message: Message, state: FSMContext):
    phone = message.text.strip()
    if len(phone) < 7:
        return await message.answer("Будь ласка, введіть коректний телефон.")
    await state.update_data(phone=phone)
    await state.set_state(OrderForm.address)
    await message.answer("🏙️ Вкажіть місто та адресу / номер відділення пошти одним повідомленням:")

@user_router.message(OrderForm.address)
async def finish_order(message: Message, state: FSMContext):
    address = message.text.strip()
    if len(address) < 5:
        return await message.answer("Будь ласка, введіть коректну адресу/відділення.")
    data = await state.get_data()
    full_name = data["full_name"]
    phone = data["phone"]

    order_id = await create_order(message.from_user.id, full_name, phone, address)
    await state.clear()

    if not order_id:
        return await message.answer("❌ Ваш кошик порожній. Додайте товари перед замовленням.")
    await message.answer(
        f"✅ Замовлення №{order_id} прийнято!\n"
        f"👤 {full_name}\n"
        f"📞 {phone}\n"
        f"📦 Доставка: {address}\n\n"
        "Наш менеджер скоро звʼяжеться з вами для підтвердження.",
        reply_markup=shop_kb
    )

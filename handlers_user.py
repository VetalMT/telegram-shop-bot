from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import Dispatcher

from keyboards import shop_kb, product_inline_kb, cart_inline_kb
from db import get_products, add_to_cart, get_cart, remove_from_cart, clear_cart, create_order

# ---------- START і базові кнопки ----------
async def cmd_start(message: types.Message):
    await message.answer("Вітаю! Оберіть дію знизу ⬇️", reply_markup=shop_kb)

async def open_catalog_from_reply(message: types.Message):
    await show_catalog(target_message=message)

async def open_cart_from_reply(message: types.Message):
    await show_cart(user_id=message.from_user.id, target_message=message)

# ---------- Каталог ----------
async def show_catalog(target_message: types.Message = None, callback: types.CallbackQuery = None):
    products = await get_products(limit=50, offset=0)
    if not products:
        text = "📭 Каталог порожній. Зверніться до адміністратора."
        if callback:
            await callback.message.answer(text)
        else:
            await target_message.answer(text)
        return

    for pid, name, desc, price, photo_id in products:
        caption = f"📦 {name}\n💰 {price} грн\n\n{desc}"
        if callback:
            if photo_id:
                await callback.message.answer_photo(photo_id, caption=caption, reply_markup=product_inline_kb(pid))
            else:
                await callback.message.answer(caption, reply_markup=product_inline_kb(pid))
        else:
            if photo_id:
                await target_message.answer_photo(photo_id, caption=caption, reply_markup=product_inline_kb(pid))
            else:
                await target_message.answer(caption, reply_markup=product_inline_kb(pid))

async def cb_open_catalog(callback: types.CallbackQuery):
    await callback.answer()
    await show_catalog(callback=callback)

# Додавання в кошик
async def cb_add_to_cart(callback: types.CallbackQuery):
    await callback.answer("✅ Додано в кошик")
    product_id = int(callback.data.split(":")[1])
    await add_to_cart(callback.from_user.id, product_id, 1)

# ---------- Кошик ----------
async def show_cart(user_id: int, target_message: types.Message = None, cq: types.CallbackQuery = None):
    items = await get_cart(user_id)
    if not items:
        text = "🛒 Ваш кошик порожній."
        if cq:
            await cq.message.answer(text)
        elif target_message:
            await target_message.answer(text)
        return

    total = sum(i["price"] * i["qty"] for i in items)
    lines = [f"• {it['name']} × {it['qty']} = {it['price']*it['qty']:.2f} грн" for it in items]
    text = "🛍 Ваш кошик:\n" + "\n".join(lines) + f"\n\nСума: {total:.2f} грн"
    kb = cart_inline_kb(items)
    if cq:
        await cq.message.answer(text, reply_markup=kb)
    else:
        await target_message.answer(text, reply_markup=kb)

async def cb_open_cart(callback: types.CallbackQuery):
    await callback.answer()
    await show_cart(callback.from_user.id, cq=callback)

async def cb_cart_remove(callback: types.CallbackQuery):
    await callback.answer("♻️ Видалено 1 шт.")
    product_id = int(callback.data.split(":")[2])
    items = await get_cart(callback.from_user.id)
    item = next((i for i in items if i["product_id"] == product_id), None)
    if not item:
        return
    if item["qty"] <= 1:
        await remove_from_cart(callback.from_user.id, product_id)
    else:
        # Реалізуємо як "мінус 1"
        await remove_from_cart(callback.from_user.id, product_id)
        await add_to_cart(callback.from_user.id, product_id, item["qty"] - 1)
    await show_cart(callback.from_user.id, cq=callback)

async def cb_cart_clear(callback: types.CallbackQuery):
    await callback.answer("🧹 Очищено")
    await clear_cart(callback.from_user.id)
    await callback.message.answer("🛒 Ваш кошик тепер порожній.")

# ---------- Оформлення замовлення (FSM) ----------
class OrderFSM(StatesGroup):
    full_name = State()
    phone = State()
    city = State()
    address = State()
    confirm = State()

async def order_start(callback: types.CallbackQuery, state: FSMContext):
    items = await get_cart(callback.from_user.id)
    if not items:
        await callback.answer()
        await callback.message.answer("🛒 Кошик порожній.")
        return
    await state.set_state(OrderFSM.full_name.state)
    await callback.answer()
    await callback.message.answer("👤 Вкажіть ваші Прізвище та Ім’я:")

async def order_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(OrderFSM.phone.state)
    await message.answer("📞 Вкажіть телефон (наприклад +380XXXXXXXXX):")

async def order_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not (phone.startswith("+") and len(phone) >= 10):
        await message.answer("❗ Невірний формат. Вкажіть телефон з + і кодом країни.")
        return
    await state.update_data(phone=phone)
    await state.set_state(OrderFSM.city.state)
    await message.answer("🏙 Вкажіть місто:")

async def order_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(OrderFSM.address.state)
    await message.answer("🏠 Вкажіть адресу доставки (вулиця, будинок, квартира):")

async def order_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    data = await state.get_data()
    confirm_text = (
        "Перевірте дані замовлення:\n"
        f"• Ім’я: {data['full_name']}\n"
        f"• Телефон: {data['phone']}\n"
        f"• Місто: {data['city']}\n"
        f"• Адреса: {data['address']}\n\n"
        "Надішліть '+' щоб підтвердити або '-' щоб скасувати."
    )
    await state.set_state(OrderFSM.confirm.state)
    await message.answer(confirm_text)

async def order_confirm(message: types.Message, state: FSMContext):
    if message.text.strip() in {"−", "-"}:
        await state.finish()
        await message.answer("❌ Оформлення скасовано.")
        return

    data = await state.get_data()
    full_address = f"{data['city']}, {data['address']}"
    order_id = await create_order(
        user_id=message.from_user.id,
        full_name=data["full_name"],
        phone=data["phone"],
        address=full_address
    )
    await state.finish()
    if order_id is None:
        await message.answer("❗ Помилка: кошик порожній.")
        return
    await message.answer(f"✅ Дякуємо за замовлення! Номер замовлення: #{order_id}")

def register_user_handlers(dp: Dispatcher):
    # Команди/кнопки
    dp.register_message_handler(cmd_start, Command("start"))
    dp.register_message_handler(open_catalog_from_reply, Text(equals=["📦 Каталог", "🛍 Каталог"]))
    dp.register_message_handler(open_cart_from_reply, Text(equals=["🛒 Корзина", "🛒 Кошик"]))

    # Каталог
    dp.register_callback_query_handler(cb_open_catalog, lambda c: c.data == "open_catalog")
    dp.register_callback_query_handler(cb_add_to_cart, lambda c: c.data and c.data.startswith("add:"))

    # Кошик
    dp.register_callback_query_handler(cb_open_cart, lambda c: c.data == "cart:open")
    dp.register_callback_query_handler(cb_cart_remove, lambda c: c.data and c.data.startswith("cart:remove:"))
    dp.register_callback_query_handler(cb_cart_clear, lambda c: c.data == "cart:clear")

    # Замовлення (FSM)
    dp.register_callback_query_handler(order_start, lambda c: c.data == "order:start", state="*")
    dp.register_message_handler(order_full_name, state=OrderFSM.full_name)
    dp.register_message_handler(order_phone, state=OrderFSM.phone)
    dp.register_message_handler(order_city, state=OrderFSM.city)
    dp.register_message_handler(order_address, state=OrderFSM.address)
    dp.register_message_handler(order_confirm, Text(equals=["+", "-", "−"]), state=OrderFSM.confirm)

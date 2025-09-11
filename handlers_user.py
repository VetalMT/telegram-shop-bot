from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import shop_kb, product_inline_kb, cart_inline_kb
from db import get_products, add_to_cart, get_cart, remove_from_cart, clear_cart, create_order

user_router = Router(name="user")

# ---------- START і базові кнопки ----------
@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Вітаю! Оберіть дію знизу ⬇️",
        reply_markup=shop_kb
    )

# Натиснута нижня кнопка "Каталог"
@user_router.message(F.text.in_(["📦 Каталог", "🛍 Каталог", "🛍 Магазин", "🛍 Каталог"]))
async def open_catalog_from_reply(message: types.Message):
    await show_catalog(message)

# Натиснута нижня кнопка "Корзина/Кошик"
@user_router.message(F.text.in_(["🛒 Корзина", "🛒 Кошик"]))
async def open_cart_from_reply(message: types.Message):
    await show_cart(message.chat.id, target_message=message)

# ---------- Каталог ----------
async def show_catalog(target: types.Message | types.CallbackQuery):
    products = await get_products(limit=50, offset=0)
    if not products:
        text = "📭 Каталог порожній. Зверніться до адміністратора."
        if isinstance(target, types.CallbackQuery):
            await target.message.answer(text)
        else:
            await target.answer(text)
        return

    for pid, name, desc, price, photo_id in products:
        caption = f"📦 {name}\n💰 {price} грн\n\n{desc}"
        if isinstance(target, types.CallbackQuery):
            if photo_id:
                await target.message.answer_photo(photo_id, caption=caption, reply_markup=product_inline_kb(pid))
            else:
                await target.message.answer(caption, reply_markup=product_inline_kb(pid))
        else:
            if photo_id:
                await target.answer_photo(photo_id, caption=caption, reply_markup=product_inline_kb(pid))
            else:
                await target.answer(caption, reply_markup=product_inline_kb(pid))

# Callback з каталогу
@user_router.callback_query(F.data == "open_catalog")
async def cb_open_catalog(callback: types.CallbackQuery):
    await callback.answer()
    await show_catalog(callback)

# Додавання в кошик
@user_router.callback_query(F.data.startswith("add:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    await callback.answer("✅ Додано в кошик")
    product_id = int(callback.data.split(":")[1])
    await add_to_cart(callback.from_user.id, product_id, 1)

# ---------- Кошик ----------
async def show_cart(user_id: int, target_message: types.Message | None = None, cq: types.CallbackQuery | None = None):
    items = await get_cart(user_id)
    if not items:
        text = "🛒 Ваш кошик порожній."
        if cq:
            await cq.message.answer(text)
        elif target_message:
            await target_message.answer(text)
        return

    total = sum(i["price"] * i["qty"] for i in items)
    lines = []
    for it in items:
        lines.append(f"• {it['name']} × {it['qty']} = {it['price']*it['qty']:.2f} грн")
    text = "🛍 Ваш кошик:\n" + "\n".join(lines) + f"\n\nСума: {total:.2f} грн"
    kb = cart_inline_kb(items)

    if cq:
        await cq.message.answer(text, reply_markup=kb)
    else:
        await target_message.answer(text, reply_markup=kb)

@user_router.callback_query(F.data == "cart:open")
async def cb_open_cart(callback: types.CallbackQuery):
    await callback.answer()
    await show_cart(callback.from_user.id, cq=callback)

@user_router.callback_query(F.data.startswith("cart:remove:"))
async def cb_cart_remove(callback: types.CallbackQuery):
    await callback.answer("♻️ Видалено 1 шт.")
    product_id = int(callback.data.split(":")[2])
    items = await get_cart(callback.from_user.id)
    item = next((i for i in items if i["product_id"] == product_id), None)
    if not item:
        return
    # зменшуємо на 1 або видаляємо повністю, якщо було 1
    if item["qty"] <= 1:
        await remove_from_cart(callback.from_user.id, product_id, qty=item["qty"])
    else:
        await remove_from_cart(callback.from_user.id, product_id, qty=1)
    await show_cart(callback.from_user.id, cq=callback)

@user_router.callback_query(F.data == "cart:clear")
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

@user_router.callback_query(F.data == "order:start")
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    items = await get_cart(callback.from_user.id)
    if not items:
        await callback.answer()
        await callback.message.answer("🛒 Кошик порожній.")
        return
    await state.set_state(OrderFSM.full_name)
    await callback.answer()
    await callback.message.answer("👤 Вкажіть ваші Прізвище та Ім’я:")

@user_router.message(OrderFSM.full_name)
async def order_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text.strip())
    await state.set_state(OrderFSM.phone)
    await message.answer("📞 Вкажіть телефон (наприклад +380XXXXXXXXX):")

@user_router.message(OrderFSM.phone)
async def order_phone(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not (phone.startswith("+") and len(phone) >= 10):
        await message.answer("❗ Невірний формат. Вкажіть телефон з + і кодом країни.")
        return
    await state.update_data(phone=phone)
    await state.set_state(OrderFSM.city)
    await message.answer("🏙 Вкажіть місто:")

@user_router.message(OrderFSM.city)
async def order_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    await state.set_state(OrderFSM.address)
    await message.answer("🏠 Вкажіть адресу доставки (вулиця, будинок, квартира):")

@user_router.message(OrderFSM.address)
async def order_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    data = await state.get_data()
    confirm_text = (
        "Перевірте дані замовлення:\n"
        f"• Ім’я: {data.get('full_name')}\n"
        f"• Телефон: {data.get('phone')}\n"
        f"• Місто: {data.get('city')}\n"
        f"• Адреса: {data.get('address')}\n\n"
        "Надішліть '+' щоб підтвердити або '-' щоб скасувати."
    )
    await state.set_state(OrderFSM.confirm)
    await message.answer(confirm_text)

@user_router.message(OrderFSM.confirm, F.text.in_({"+", "-"}))
async def order_confirm(message: types.Message, state: FSMContext):
    if message.text.strip() == "-":
        await state.clear()
        await message.answer("❌ Оформлення скасовано.")
        return

    data = await state.get_data()
    full_address = f"{data.get('city')}, {data.get('address')}"
    order_id = await create_order(
        user_id=message.from_user.id,
        full_name=data.get("full_name"),
        phone=data.get("phone"),
        address=full_address
    )
    await state.clear()
    if order_id is None:
        await message.answer("❗ Помилка: кошик порожній.")
        return
    await message.answer(f"✅ Дякуємо за замовлення! Номер замовлення: #{order_id}")

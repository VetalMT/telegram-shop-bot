from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from keyboards import main_kb, product_inline_kb, cart_inline_kb
from db import get_products, add_to_cart, get_cart, remove_from_cart, clear_cart, create_order

# FSM for order
class OrderFSM(StatesGroup):
    full_name = State()
    phone = State()
    city = State()
    address = State()
    confirm = State()

def register_user(dp: Dispatcher):
    @dp.message_handler(commands=["start"])
    async def cmd_start(message: types.Message):
        await message.answer("Вітаю! Оберіть дію знизу ⬇️", reply_markup=main_kb())

    @dp.message_handler(lambda m: m.text in ["📦 Каталог", "🛍 Каталог"])
    async def open_catalog_from_reply(message: types.Message):
        products = await get_products()
        if not products:
            await message.answer("📭 Каталог порожній. Зверніться до адміністратора.")
            return
        for pid, name, desc, price, photo_id in products:
            caption = f"📦 {name}\n💰 {price} грн\n\n{desc}"
            if photo_id:
                await message.answer_photo(photo_id, caption=caption, reply_markup=product_inline_kb(pid))
            else:
                await message.answer(caption, reply_markup=product_inline_kb(pid))

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith("add:"))
    async def cb_add_to_cart(callback: types.CallbackQuery):
        await callback.answer("✅ Додано в кошик")
        product_id = int(callback.data.split(":")[1])
        await add_to_cart(callback.from_user.id, product_id, 1)

    @dp.callback_query_handler(lambda c: c.data == "cart:open")
    async def cb_open_cart(callback: types.CallbackQuery):
        await callback.answer()
        await _show_cart(callback.from_user.id, callback.message, callback)

    async def _show_cart(user_id: int, target_message: types.Message | None = None, cq: types.CallbackQuery | None = None):
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

    @dp.callback_query_handler(lambda c: c.data and c.data.startswith("cart:remove:"))
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
            # Зменшуємо кількість на 1
            await add_to_cart(callback.from_user.id, product_id, -1)
        await _show_cart(callback.from_user.id, cq=callback)

    @dp.callback_query_handler(lambda c: c.data == "cart:clear")
    async def cb_cart_clear(callback: types.CallbackQuery):
        await callback.answer("🧹 Очищено")
        await clear_cart(callback.from_user.id)
        await callback.message.answer("🛒 Ваш кошик тепер порожній.")

    @dp.callback_query_handler(lambda c: c.data == "order:start")
    async def order_start(callback: types.CallbackQuery):
        items = await get_cart(callback.from_user.id)
        if not items:
            await callback.answer()
            await callback.message.answer("🛒 Кошик порожній.")
            return
        await OrderFSM.full_name.set()
        await callback.answer()
        await callback.message.answer("👤 Вкажіть ваші Прізвище та Ім’я:")

    @dp.message_handler(state=OrderFSM.full_name)
    async def order_full_name(message: types.Message, state: FSMContext):
        await state.update_data(full_name=message.text.strip())
        await OrderFSM.next()
        await message.answer("📞 Вкажіть телефон (наприклад +380XXXXXXXXX):")

    @dp.message_handler(state=OrderFSM.phone)
    async def order_phone(message: types.Message, state: FSMContext):
        phone = message.text.strip()
        if not (phone.startswith("+") and len(phone) >= 10):
            await message.answer("❗ Невірний формат. Введіть телефон з + і кодом країни.")
            return
        await state.update_data(phone=phone)
        await OrderFSM.next()
        await message.answer("🏙 Вкажіть місто:")

    @dp.message_handler(state=OrderFSM.city)
    async def order_city(message: types.Message, state: FSMContext):
        await state.update_data(city=message.text.strip())
        await OrderFSM.next()
        await message.answer("🏠 Вкажіть адресу доставки (вулиця, будинок, квартира):")

    @dp.message_handler(state=OrderFSM.address)
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
        await OrderFSM.confirm.set()
        await message.answer(confirm_text)

    @dp.message_handler(lambda m: m.text in {"+", "−", "-"}, state=OrderFSM.confirm)
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
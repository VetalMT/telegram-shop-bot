# handlers_user.py
import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import shop_kb, product_inline_kb, cart_inline_kb
from db import (
    get_products,
    add_to_cart,
    get_cart,
    remove_from_cart,
    clear_cart,
    create_order,
)

logger = logging.getLogger(__name__)
user_router = Router(name="user")

# ---------- START і базові кнопки ----------
@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Вітаю! Оберіть дію знизу ⬇️",
        reply_markup=shop_kb
    )

# Натиснута нижня кнопка "Каталог" (reply-кнопка)
@user_router.message(F.text.in_(["📦 Каталог", "🛍 Каталог", "🛍 Магазин", "🛍 Каталог"]))
async def open_catalog_from_reply(message: types.Message):
    await show_catalog(message)

# Натиснута нижня кнопка "Корзина/Кошик" (reply-кнопка)
@user_router.message(F.text.in_(["🛒 Корзина", "🛒 Кошик"]))
async def open_cart_from_reply(message: types.Message):
    await show_cart(message.chat.id, target_message=message)


# ---------- Каталог ----------
async def show_catalog(target: types.Message | types.CallbackQuery):
    """
    Відправляє список товарів як повідомлення/фото з інлайн-кнопками.
    target може бути Message або CallbackQuery.
    """
    try:
        products = await get_products(limit=50, offset=0)
    except Exception as e:
        logger.exception("Помилка get_products(): %s", e)
        text = "❗ Помилка при отриманні каталогу. Спробуйте пізніше."
        if isinstance(target, types.CallbackQuery):
            await target.message.answer(text)
        else:
            await target.answer(text)
        return

    if not products:
        text = "📭 Каталог порожній. Зверніться до адміністратора."
        if isinstance(target, types.CallbackQuery):
            await target.message.answer(text)
        else:
            await target.answer(text)
        return

    # Відправляємо по одному товару
    for pid, name, desc, price, photo_id in products:
        caption = f"📦 <b>{name}</b>\n💰 <b>{price:.2f} грн</b>\n\n{desc}"
        try:
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
        except Exception as e:
            logger.exception("Не вдалося відправити товар #%s: %s", pid, e)


# Callback з каталогу (наприклад, інша інлайн-кнопка відкриття каталогу)
@user_router.callback_query(F.data == "open_catalog")
async def cb_open_catalog(callback: types.CallbackQuery):
    await callback.answer()  # приховуємо спінер
    await show_catalog(callback)


# ---------- Додавання в кошик ----------
@user_router.callback_query(F.data.startswith("add:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    """
    Очікуємо callback.data формату "add:<product_id>"
    """
    await callback.answer()  # одразу прибираємо спінер у клієнті
    try:
        product_id = int(callback.data.split(":", 1)[1])
    except Exception as e:
        logger.exception("Невірний формат callback.data для add_to_cart: %s", callback.data)
        await callback.message.answer("❗ Невірний формат даних кнопки.")
        return

    try:
        # додаємо в кошик
        await add_to_cart(callback.from_user.id, product_id, 1)
        # надсилаємо невелике підтвердження (toast)
        await callback.answer("✅ Додано в кошик", show_alert=False)
        logger.info("Користувач %s додав товар #%s у кошик", callback.from_user.id, product_id)
    except Exception as e:
        logger.exception("Помилка add_to_cart user=%s product=%s: %s", callback.from_user.id, product_id, e)
        # показуємо alert з помилкою
        try:
            await callback.answer("⚠️ Невдалось додати в кошик. Спробуйте пізніше.", show_alert=True)
        except Exception:
            pass


# ---------- Кошик ----------
async def show_cart(user_id: int, target_message: types.Message | None = None, cq: types.CallbackQuery | None = None):
    """
    Показати кошик користувача. Якщо cq передано — відповідь у тому ж чаті.
    """
    try:
        items = await get_cart(user_id)
    except Exception as e:
        logger.exception("Помилка get_cart() для user %s: %s", user_id, e)
        text = "❗ Неможливо отримати кошик. Спробуйте пізніше."
        if cq:
            await cq.message.answer(text)
        elif target_message:
            await target_message.answer(text)
        return

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

    try:
        if cq:
            await cq.message.answer(text, reply_markup=kb)
        else:
            await target_message.answer(text, reply_markup=kb)
    except Exception as e:
        logger.exception("Не вдалося відправити кошик user=%s: %s", user_id, e)


@user_router.callback_query(F.data == "cart:open")
async def cb_open_cart(callback: types.CallbackQuery):
    # прибираємо спінер
    await callback.answer()
    await show_cart(callback.from_user.id, cq=callback)


@user_router.callback_query(F.data.startswith("cart:remove:"))
async def cb_cart_remove(callback: types.CallbackQuery):
    """
    callback.data = "cart:remove:<product_id>"
    Зменшує кількість на 1 або видаляє, потім оновлює кошик.
    """
    await callback.answer()  # прибираємо "завантаження"
    try:
        product_id = int(callback.data.split(":", 2)[2])
    except Exception as e:
        logger.exception("Помилка парсингу product_id в cart:remove: %s", callback.data)
        await callback.answer("❗ Невірні дані кнопки", show_alert=True)
        return

    try:
        # отримуємо поточні позиції щоб визначити qty (get_cart)
        items = await get_cart(callback.from_user.id)
        item = next((i for i in items if i["product_id"] == product_id), None)
        if not item:
            # нічого не робимо
            await callback.answer("🟡 Товар вже відсутній у кошику", show_alert=False)
            await show_cart(callback.from_user.id, cq=callback)
            return

        # зменшуємо на 1 (remove_from_cart має параметр qty)
        if item["qty"] <= 1:
            await remove_from_cart(callback.from_user.id, product_id, qty=item["qty"])
        else:
            await remove_from_cart(callback.from_user.id, product_id, qty=1)

        await callback.answer("♻️ Оновлено кошик", show_alert=False)
        await show_cart(callback.from_user.id, cq=callback)
        logger.info("Користувач %s видалив/зменшив товар %s у кошику", callback.from_user.id, product_id)
    except Exception as e:
        logger.exception("Помилка при видаленні з кошика user=%s product=%s: %s", callback.from_user.id, product_id, e)
        try:
            await callback.answer("⚠️ Сталася помилка при оновленні кошика", show_alert=True)
        except Exception:
            pass


@user_router.callback_query(F.data == "cart:clear")
async def cb_cart_clear(callback: types.CallbackQuery):
    await callback.answer()  # прибираємо спінер
    try:
        await clear_cart(callback.from_user.id)
        await callback.message.answer("🧹 Ваш кошик очищено.")
        logger.info("Користувач %s очистив кошик", callback.from_user.id)
    except Exception as e:
        logger.exception("Помилка clear_cart user=%s: %s", callback.from_user.id, e)
        try:
            await callback.answer("⚠️ Не вдалося очистити кошик", show_alert=True)
        except Exception:
            pass


# ---------- Оформлення замовлення (FSM) ----------
class OrderFSM(StatesGroup):
    full_name = State()
    phone = State()
    city = State()
    address = State()
    confirm = State()

@user_router.callback_query(F.data == "order:start")
async def order_start(callback: types.CallbackQuery, state: FSMContext):
    # приховуємо спінер
    await callback.answer()
    items = await get_cart(callback.from_user.id)
    if not items:
        await callback.message.answer("🛒 Кошик порожній.")
        return
    await state.set_state(OrderFSM.full_name)
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
        await message.answer("❗ Невірний формат. Введіть телефон з кодом країни, напр. +380XXXXXXXXX")
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

@user_router.message(OrderFSM.confirm, F.text.in_({"+", "−", "-"}))
async def order_confirm(message: types.Message, state: FSMContext):
    if message.text.strip() in {"−", "-"}:
        await state.clear()
        await message.answer("❌ Оформлення скасовано.")
        return

    data = await state.get_data()
    full_address = f"{data.get('city')}, {data.get('address')}"
    try:
        order_id = await create_order(
            user_id=message.from_user.id,
            full_name=data.get("full_name"),
            phone=data.get("phone"),
            address=full_address
        )
    except Exception as e:
        logger.exception("Помилка create_order user=%s: %s", message.from_user.id, e)
        await message.answer("❗ Помилка при створенні замовлення. Спробуйте пізніше.")
        await state.clear()
        return

    await state.clear()
    if order_id is None:
        await message.answer("❗ Помилка: кошик порожній.")
        return
    await message.answer(f"✅ Дякуємо за замовлення! Номер замовлення: #{order_id}")

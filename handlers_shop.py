from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import shop_kb, product_inline_kb, products_pagination_kb, cart_inline_kb
from db import get_products, count_products, add_to_cart, get_cart, clear_cart, remove_from_cart, create_order, get_product
from config import ADMIN_ID

shop_router = Router()

PAGE_SIZE = 5  # скільки товарів показуємо на сторінку (списком)

class OrderFSM(StatesGroup):
    name = State()
    phone = State()
    address = State()

@shop_router.message(CommandStart())
async def start(msg: Message):
    await msg.answer("👋 Привіт! Це магазин у Telegram. Обери дію:", reply_markup=shop_kb)

@shop_router.message(F.text == "🛍 Каталог")
async def open_catalog(msg: Message):
    await show_page(msg, page=0)

async def show_page(obj, page: int):
    total = await count_products()
    if total == 0:
        if hasattr(obj, "answer"):
            return await obj.answer("Каталог порожній. Спробуй пізніше.")
        else:
            return await obj.message.answer("Каталог порожній. Спробуй пізніше.")
    offset = page * PAGE_SIZE
    items = await get_products(limit=PAGE_SIZE, offset=offset)
    has_prev = page > 0
    has_next = (offset + PAGE_SIZE) < total

    text_lines = [f"<b>Каталог (стор. {page+1})</b>"]
    for pid, name, description, price, photo_id in items:
        text_lines.append(f"• <b>{name}</b> — {price:.2f} ₴ (#{pid})")

    kb = products_pagination_kb(page, has_prev, has_next)

    if hasattr(obj, "answer"):
        await obj.answer("\n".join(text_lines), parse_mode="HTML", reply_markup=kb)
    else:
        await obj.message.edit_text("\n".join(text_lines), parse_mode="HTML", reply_markup=kb)

@shop_router.callback_query(F.data.startswith("page:"))
async def page_cb(cb: CallbackQuery):
    page = int(cb.data.split(":")[1])
    await show_page(cb, page)

# Клік по товару з каталогу: користувач вводить id
@shop_router.message(F.text.regexp(r"^#\d+$"))
async def open_product_by_hash(msg: Message):
    pid = int(msg.text[1:])
    row = await get_product(pid)
    if not row:
        return await msg.answer("Товар не знайдено.")
    pid, name, description, price, photo_id = row
    caption = f"<b>{name}</b>\n{description}\n\nЦіна: {price:.2f} ₴"
    if photo_id:
        await msg.answer_photo(photo=photo_id, caption=caption, parse_mode="HTML",
                               reply_markup=product_inline_kb(pid))
    else:
        await msg.answer(caption, parse_mode="HTML", reply_markup=product_inline_kb(pid))

# Додавання в кошик
@shop_router.callback_query(F.data.startswith("add:"))
async def add_to_cart_cb(cb: CallbackQuery):
    pid = int(cb.data.split(":")[1])
    await add_to_cart(cb.from_user.id, pid, qty=1)
    await cb.answer("Додано до кошика ✅", show_alert=False)

# Відкрити кошик
@shop_router.message(F.text == "🛒 Кошик")
@shop_router.callback_query(F.data == "cart:open")
async def open_cart(obj):
    user_id = obj.from_user.id if isinstance(obj, CallbackQuery) else obj.from_user.id
    items = await get_cart(user_id)
    if not items:
        if isinstance(obj, CallbackQuery):
            return await obj.message.answer("Кошик порожній.")
        return await obj.answer("Кошик порожній.")
    total = sum(i["price"] * i["qty"] for i in items)
    lines = ["<b>Ваш кошик:</b>"]
    for i in items:
        lines.append(f"• {i['name']} × {i['qty']} = {i['price']*i['qty']:.2f} ₴")
    lines.append(f"\n<b>Разом:</b> {total:.2f} ₴")
    reply_kb = cart_inline_kb()
    if isinstance(obj, CallbackQuery):
        await obj.message.answer("\n".join(lines), parse_mode="HTML", reply_markup=reply_kb)
    else:
        await obj.answer("\n".join(lines), parse_mode="HTML", reply_markup=reply_kb)

# Очистити кошик
@shop_router.callback_query(F.data == "cart:clear")
async def clear_cart_cb(cb: CallbackQuery):
    await clear_cart(cb.from_user.id)
    await cb.message.edit_text("🧹 Кошик очищено.")

# Оформлення замовлення
@shop_router.callback_query(F.data == "order:start")
async def order_start(cb: CallbackQuery, state: FSMContext):
    items = await get_cart(cb.from_user.id)
    if not items:
        return await cb.answer("Кошик порожній", show_alert=True)
    await state.set_state(OrderFSM.name)
    await cb.message.answer("Вкажіть ПІБ:")

@shop_router.message(OrderFSM.name)
async def order_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text.strip())
    await state.set_state(OrderFSM.phone)
    await msg.answer("Телефон:")

@shop_router.message(OrderFSM.phone)
async def order_phone(msg: Message, state: FSMContext):
    await state.update_data(phone=msg.text.strip())
    await state.set_state(OrderFSM.address)
    await msg.answer("Адреса доставки:")

@shop_router.message(OrderFSM.address)
async def order_finish(msg: Message, state: FSMContext):
    data = await state.get_data()
    order_id = await create_order(
        user_id=msg.from_user.id,
        full_name=data["name"],
        phone=data["phone"],
        address=msg.text.strip()
    )
    await state.clear()
    if not order_id:
        return await msg.answer("Кошик порожній.")
    await msg.answer(f"✅ Замовлення #{order_id} прийнято! Менеджер зв'яжеться з вами.")
    # Повідомляємо адміна
    try:
        await msg.bot.send_message(
            ADMIN_ID,
            f"🆕 Нове замовлення #{order_id}\n"
            f"Клієнт: {data['name']}\nТелефон: {data['phone']}\nАдреса: {msg.text.strip()}"
        )
    except Exception:
        pass

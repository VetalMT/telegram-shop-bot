from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import db

router = Router()


class OrderFSM(StatesGroup):
    name = State()
    phone = State()
    city = State()
    address = State()


# ================== START ==================
@router.message(Command("start"))
async def start(message: types.Message):
    keyboard = [
        [types.KeyboardButton(text="🛍 Каталог")],
        [types.KeyboardButton(text="🛒 Кошик")],
        [types.KeyboardButton(text="✅ Оформити замовлення")],
    ]
    markup = types.ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    await message.answer("Ласкаво просимо в магазин!", reply_markup=markup)


# ================== CATALOG ==================
@router.message(lambda m: m.text == "🛍 Каталог")
async def catalog(message: types.Message, pool):
    products = await db.get_products(pool)
    if not products:
        return await message.answer("Немає товарів")
    for p in products:
        kb = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="➕ У кошик", callback_data=f"add_{p['id']}")]
        ])
        await message.answer_photo(photo=p["photo"], caption=f"{p['name']}\n{p['description']}\n💰 {p['price']} грн", reply_markup=kb)


@router.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart_callback(call: types.CallbackQuery, pool):
    product_id = int(call.data.split("_")[1])
    await db.add_to_cart(pool, call.from_user.id, product_id)
    await call.answer("✅ Додано у кошик", show_alert=False)


# ================== CART ==================
@router.message(lambda m: m.text == "🛒 Кошик")
async def cart(message: types.Message, pool):
    items = await db.get_cart(pool, message.from_user.id)
    if not items:
        return await message.answer("Ваш кошик порожній")
    text = "Ваш кошик:\n"
    kb = types.InlineKeyboardMarkup(inline_keyboard=[])
    for i in items:
        text += f"{i['id']}. {i['name']} - {i['price']} грн\n"
        kb.inline_keyboard.append([types.InlineKeyboardButton(text=f"❌ Видалити {i['name']}", callback_data=f"del_{i['id']}")])
    await message.answer(text, reply_markup=kb)


@router.callback_query(lambda c: c.data.startswith("del_"))
async def remove_from_cart_callback(call: types.CallbackQuery, pool):
    cart_id = int(call.data.split("_")[1])
    await db.remove_from_cart(pool, cart_id)
    await call.answer("❌ Видалено")
    await call.message.delete()


# ================== ORDER ==================
@router.message(lambda m: m.text == "✅ Оформити замовлення")
async def order_start(message: types.Message, state: FSMContext):
    await state.set_state(OrderFSM.name)
    await message.answer("Введіть ваше ім'я:")


@router.message(OrderFSM.name)
async def order_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderFSM.phone)
    await message.answer("Введіть ваш телефон:")


@router.message(OrderFSM.phone)
async def order_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(OrderFSM.city)
    await message.answer("Введіть ваше місто:")


@router.message(OrderFSM.city)
async def order_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(OrderFSM.address)
    await message.answer("Введіть вашу адресу:")


@router.message(OrderFSM.address)
async def order_address(message: types.Message, state: FSMContext, pool):
    data = await state.get_data()
    order_id = await db.create_order(pool, message.from_user.id, data["name"], data["phone"], data["city"], message.text)

    items = await db.get_cart(pool, message.from_user.id)
    for i in items:
        await db.add_order_item(pool, order_id, i["id"])
    await db.clear_cart(pool, message.from_user.id)

    await state.clear()
    await message.answer("✅ Замовлення оформлено! Очікуйте дзвінка менеджера.")

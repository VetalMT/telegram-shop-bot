from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user_router = Router()

# 🛒 Тимчасове сховище кошиків (демо)
user_carts = {}

def add_to_cart(user_id: int, product_id: str):
    user_carts.setdefault(user_id, []).append(product_id)

# --- Старт ---
@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Каталог", callback_data="open_catalog")],
            [InlineKeyboardButton(text="🛒 Кошик", callback_data="open_cart")],
        ]
    )
    await message.answer("Вітаю! Оберіть дію:", reply_markup=keyboard)

# --- Каталог ---
@user_router.callback_query(F.data == "open_catalog")
async def cb_open_catalog(callback: types.CallbackQuery):
    await callback.answer()

    products = [
        {"id": "1", "name": "Товар 1", "price": 100},
        {"id": "2", "name": "Товар 2", "price": 200},
    ]

    for product in products:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🛒 Додати в кошик", callback_data=f"add_to_cart:{product['id']}")]
            ]
        )
        await callback.message.answer(
            f"📦 {product['name']}\n💰 Ціна: {product['price']} грн",
            reply_markup=keyboard
        )

# --- Додавання в кошик ---
@user_router.callback_query(F.data.startswith("add_to_cart:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    product_id = callback.data.split(":", 1)[1]
    add_to_cart(callback.from_user.id, product_id)
    await callback.answer("✅ Додано в кошик")

# --- Перегляд кошика ---
@user_router.callback_query(F.data == "open_cart")
async def cb_open_cart(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await callback.message.answer("🛒 Ваш кошик порожній.")
        return

    text = "🛍 Ваш кошик:\n" + "\n".join([f"Товар {item}" for item in cart])
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Очистити", callback_data="clear_cart")],
            [InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="checkout")],
        ]
    )
    await callback.message.answer(text, reply_markup=keyboard)

# --- Очистка кошика ---
@user_router.callback_query(F.data == "clear_cart")
async def cb_clear_cart(callback: types.CallbackQuery):
    user_carts[callback.from_user.id] = []
    await callback.answer("🗑 Кошик очищено")
    await callback.message.answer("🛒 Ваш кошик тепер порожній.")

# --- Оформлення замовлення ---
@user_router.callback_query(F.data == "checkout")
async def cb_checkout(callback: types.CallbackQuery):
    user_carts[callback.from_user.id] = []
    await callback.answer("✅ Замовлення оформлено")
    await callback.message.answer("Дякуємо за замовлення! 💙")

# --- Фолбек, щоб не було 'not handled' ---
@user_router.message()
async def fallback(message: types.Message):
    # Перенаправляємо користувача в стартове меню
    await cmd_start(message)

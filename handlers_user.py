from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

user_router = Router()

# 🛒 Тимчасове сховище кошиків
user_carts = {}

def add_to_cart(user_id: int, product_id: str):
    if user_id not in user_carts:
        user_carts[user_id] = []
    user_carts[user_id].append(product_id)

# 📌 Стартове меню
@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Каталог", callback_data="open_catalog")],
            [InlineKeyboardButton(text="🛒 Кошик", callback_data="open_cart")],
        ]
    )
    await message.answer("Вітаю! Оберіть дію:", reply_markup=keyboard)

# 📌 Відкриття каталогу
@user_router.callback_query(F.data == "open_catalog")
async def cb_open_catalog(callback: types.CallbackQuery):
    await callback.answer()

    # Тестові товари
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

# 📌 Додавання в кошик
@user_router.callback_query(F.data.startswith("add_to_cart:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    await callback.answer("✅ Додано в кошик")
    product_id = callback.data.split(":")[1]
    add_to_cart(callback.from_user.id, product_id)

# 📌 Перегляд кошика
@user_router.callback_query(F.data == "open_cart")
async def cb_open_cart(callback: types.CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await callback.message.answer("🛒 Ваш кошик порожній.")
    else:
        text = "🛍 Ваш кошик:\n" + "\n".join([f"Товар {item}" for item in cart])
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="❌ Очистити", callback_data="clear_cart")],
                [InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="checkout")],
            ]
        )
        await callback.message.answer(text, reply_markup=keyboard)

# 📌 Очистка кошика
@user_router.callback_query(F.data == "clear_cart")
async def cb_clear_cart(callback: types.CallbackQuery):
    await callback.answer("🗑 Кошик очищено")
    user_carts[callback.from_user.id] = []
    await callback.message.answer("🛒 Ваш кошик тепер порожній.")

# 📌 Оформлення замовлення
@user_router.callback_query(F.data == "checkout")
async def cb_checkout(callback: types.CallbackQuery):
    await callback.answer("✅ Замовлення оформлено")
    user_carts[callback.from_user.id] = []
    await callback.message.answer("Дякуємо за замовлення! 💙")

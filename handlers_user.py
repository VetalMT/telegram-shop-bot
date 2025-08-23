# handlers_user.py
from aiogram import Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_router = Router()

# 🛒 Тимчасове сховище кошиків (можна замінити на БД)
user_carts = {}

# 📌 Функція додавання в кошик
def add_to_cart(user_id: int, product_id: str):
    if user_id not in user_carts:
        user_carts[user_id] = []
    user_carts[user_id].append(product_id)


# 📌 Стартове меню
@user_router.message(commands=["start"])
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍 Каталог", callback_data="open_catalog")],
            [InlineKeyboardButton(text="🛒 Кошик", callback_data="open_cart")],
        ]
    )
    await message.answer("Вітаю! Оберіть дію:", reply_markup=keyboard)


# 📌 Відкриття каталогу (поки що демо-товари)
@user_router.callback_query(lambda c: c.data == "open_catalog")
async def cb_open_catalog(callback: types.CallbackQuery):
    await callback.answer()  # ⚡ миттєва відповідь, щоб не було помилки

    # Тестові товари (можна брати з БД)
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
@user_router.callback_query(lambda c: c.data.startswith("add_to_cart:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    await callback.answer("✅ Додано в кошик")  # ⚡ миттєво відповідаємо

    product_id = callback.data.split(":")[1]
    user_id = callback.from_user.id
    add_to_cart(user_id, product_id)


# 📌 Перегляд кошика
@user_router.callback_query(lambda c: c.data == "open_cart")
async def cb_open_cart(callback: types.CallbackQuery):
    await callback.answer()  # ⚡ миттєва відповідь

    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])

    if not cart:
        await callback.message.answer("🛒 Ваш кошик порожній.")
    else:
        text = "🛍 Ваш кошик:\n" + "\n".join([f"Товар {item}" for item in cart])
        await callback.message.answer(text)

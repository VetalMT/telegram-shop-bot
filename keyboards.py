from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

shop_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Переглянути товари")],
        [KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📦 Переглянути товари")]
    ],
    resize_keyboard=True
)

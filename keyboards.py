from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавіатура для користувача
shop_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🛍 Переглянути товари")],
        [KeyboardButton(text="🛒 Корзина")]
    ],
    resize_keyboard=True
)

# Клавіатура для адміністратора
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📦 Переглянути товари")]
    ],
    resize_keyboard=True
)

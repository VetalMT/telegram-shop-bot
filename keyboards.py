from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавіатура для користувача
shop_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="🛍 Переглянути товари")],
        [KeyboardButton(text="🛒 Корзина")]
    ]
)

# Клавіатура для адміна
admin_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📦 Переглянути товари")]
    ]
)

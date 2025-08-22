from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавіатура для користувача
shop_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("🛍 Переглянути товари")],
        [KeyboardButton("🛒 Корзина")]
    ],
    resize_keyboard=True
)

# Клавіатура для адміна
admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("➕ Додати товар")],
        [KeyboardButton("❌ Видалити товар")],
        [KeyboardButton("📦 Переглянути товари")]
    ],
    resize_keyboard=True
)

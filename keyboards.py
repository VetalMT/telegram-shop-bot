from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# ========================
# Клавіатура для користувача
# ========================

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🛍 Магазин"),
            KeyboardButton(text="ℹ️ Допомога")
        ],
        [
            KeyboardButton(text="📦 Мої замовлення")
        ]
    ],
    resize_keyboard=True
)

# ========================
# Клавіатура для адміна
# ========================

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Додати товар"),
            KeyboardButton(text="📋 Список товарів")
        ],
        [
            KeyboardButton(text="📊 Статистика"),
            KeyboardButton(text="👥 Користувачі")
        ]
    ],
    resize_keyboard=True
)

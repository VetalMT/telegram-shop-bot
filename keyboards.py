from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Меню користувача
shop_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="🛍 Каталог")],
        [KeyboardButton(text="🛒 Кошик")]
    ]
)

# Меню адміна
admin_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📦 Переглянути товари")]
    ]
)

def product_inline_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Додати у кошик", callback_data=f"add:{product_id}")
    kb.button(text="🛒 Перейти в кошик", callback_data="cart:open")
    kb.adjust(1)
    return kb.as_markup()

def cart_inline_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🧹 Очистити", callback_data="cart:clear")
    kb.button(text="✅ Оформити замовлення", callback_data="order:start")
    kb.adjust(2)
    return kb.as_markup()

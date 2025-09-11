from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Меню користувача (reply-кнопки внизу)
shop_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="📦 Каталог")],
        [KeyboardButton(text="🛒 Кошик")]
    ]
)

# Меню адміна (reply-кнопки внизу)
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
    kb.button(text="🛒 Відкрити кошик", callback_data="cart:open")
    kb.adjust(1)
    return kb.as_markup()

def cart_inline_kb(items: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    # Кнопки видалення для кожного товару
    for it in items:
        kb.button(text=f"❌ {it['name']} (–1)", callback_data=f"cart:remove:{it['product_id']}")
    if items:
        kb.button(text="🧹 Очистити все", callback_data="cart:clear")
        kb.button(text="✅ Оформити замовлення", callback_data="order:start")
    kb.adjust(1)
    return kb.as_markup()

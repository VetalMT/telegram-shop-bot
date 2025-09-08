from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Меню користувача (reply-кнопки)
shop_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="🛍 Каталог")],
        [KeyboardButton(text="🛒 Кошик")]
    ]
)

# Меню адміна (reply-кнопки)
admin_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📦 Переглянути товари")]
    ]
)

def product_inline_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text="➕ Додати у кошик", callback_data=f"add:{product_id}"))
    kb.add(InlineKeyboardButton(text="🛒 Відкрити кошик", callback_data="cart:open"))
    return kb

def cart_inline_kb(items: list) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    for it in items:
        kb.add(InlineKeyboardButton(
            text=f"❌ {it['name']} (–1)",
            callback_data=f"cart:remove:{it['product_id']}"
        ))
    if items:
        kb.add(InlineKeyboardButton(text="🧹 Очистити все", callback_data="cart:clear"))
        kb.add(InlineKeyboardButton(text="✅ Оформити замовлення", callback_data="order:start"))
    return kb

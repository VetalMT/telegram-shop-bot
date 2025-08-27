from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📦 Каталог"), KeyboardButton("🛒 Кошик"))
    return kb

def admin_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("➕ Додати товар"))
    kb.add(KeyboardButton("❌ Видалити товар"))
    kb.add(KeyboardButton("📋 Переглянути товари"))
    return kb

def product_inline_kb(product_id: int):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Додати у кошик", callback_data=f"add:{product_id}"))
    kb.add(InlineKeyboardButton("🛒 Переглянути кошик", callback_data="cart:view"))
    return kb

def cart_inline_kb(items):
    kb = InlineKeyboardMarkup()
    for it in items:
        kb.add(InlineKeyboardButton(f"❌ {it['name']} (–1)", callback_data=f"cart:remove:{it['product_id']}"))
    if items:
        kb.add(InlineKeyboardButton("🧹 Очистити все", callback_data="cart:clear"))
        kb.add(InlineKeyboardButton("✅ Оформити замовлення", callback_data="order:start"))
    return kb
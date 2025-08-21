from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("🛒 Товари"))
    kb.add(KeyboardButton("📦 Корзина"))
    kb.add(KeyboardButton("⚙️ Адмін-панель"))
    return kb

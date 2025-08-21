
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

shop_kb = ReplyKeyboardMarkup(resize_keyboard=True)
shop_kb.add(KeyboardButton("🛍 Переглянути товари"))
shop_kb.add(KeyboardButton("🛒 Корзина"))

admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(KeyboardButton("➕ Додати товар"))
admin_kb.add(KeyboardButton("❌ Видалити товар"))
admin_kb.add(KeyboardButton("📦 Переглянути товари"))

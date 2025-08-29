from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def user_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог"), KeyboardButton(text="Кошик")]
        ],
        resize_keyboard=True
    )

def admin_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Додати товар")],
            [KeyboardButton(text="Видалити товар")],
            [KeyboardButton(text="Переглянути товари")]
        ],
        resize_keyboard=True
    )

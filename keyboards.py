from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Кнопки покупця
catalog_button = InlineKeyboardMarkup(row_width=1)
catalog_button.add(InlineKeyboardButton(text="Каталог", callback_data="show_catalog"))
catalog_button.add(InlineKeyboardButton(text="Кошик", callback_data="show_cart"))

# Кнопки адміна
admin_keyboard = InlineKeyboardMarkup(row_width=1)
admin_keyboard.add(InlineKeyboardButton(text="Додати товар", callback_data="add_product"))
admin_keyboard.add(InlineKeyboardButton(text="Видалити товар", callback_data="delete_product"))
admin_keyboard.add(InlineKeyboardButton(text="Переглянути товари", callback_data="list_products"))

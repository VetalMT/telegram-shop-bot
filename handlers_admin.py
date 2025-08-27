from aiogram import Router, types
from aiogram.filters import Command
from db import add_item, delete_item, get_items

admin_router = Router()

# Головне меню адміна
@admin_router.message(Command("admin"))
async def admin_panel(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Додати товар")],
            [types.KeyboardButton(text="🗑 Видалити товар")],
            [types.KeyboardButton(text="📦 Переглянути товари")]
        ],
        resize_keyboard=True
    )
    await message.answer("Адмін-панель. Виберіть дію:", reply_markup=keyboard)


# Додати товар
@admin_router.message(lambda m: m.text == "➕ Додати товар")
async def add_item_start(message: types.Message):
    await message.answer("Введіть назву та ціну товару через кому:\nНаприклад: Телефон, 5000")


@admin_router.message(lambda m: "," in m.text and m.text.count(",") == 1)
async def add_item_process(message: types.Message):
    try:
        name, price = message.text.split(",")
        add_item(name.strip(), float(price.strip()))
        await message.answer(f"✅ Товар *{name.strip()}* додано за {price.strip()} грн", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")


# Видалити товар
@admin_router.message(lambda m: m.text == "🗑 Видалити товар")
async def delete_item_start(message: types.Message):
    await message.answer("Введіть ID товару для видалення:")


@admin_router.message(lambda m: m.text.isdigit())
async def delete_item_process(message: types.Message):
    try:
        item_id = int(message.text)
        delete_item(item_id)
        await message.answer(f"🗑 Товар з ID {item_id} видалено")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")


# Переглянути товари
@admin_router.message(lambda m: m.text == "📦 Переглянути товари")
async def view_items(message: types.Message):
    items = get_items()
    if not items:
        await message.answer("📭 Товарів ще немає")
        return

    text = "📦 Список товарів:\n\n"
    for item in items:
        text += f"ID: {item['id']} | {item['name']} — {item['price']} грн\n"

    await message.answer(text)
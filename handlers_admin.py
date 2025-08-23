from aiogram import Router, types, F
from aiogram.filters import Command
from config import ADMIN_ID

admin_router = Router()

@admin_router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас немає прав адміністратора.")
        return

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="➕ Додати товар")],
            [types.KeyboardButton(text="❌ Видалити товар")],
            [types.KeyboardButton(text="📦 Переглянути товари")],
        ],
        resize_keyboard=True
    )
    await message.answer("⚙️ Адмін-панель", reply_markup=keyboard)

@admin_router.message(F.text == "➕ Додати товар")
async def admin_add_product(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("📸 Надішліть фото товару (поки демо).")

@admin_router.message(F.text == "❌ Видалити товар")
async def admin_delete_product(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Видалення товарів ще не реалізовано (демо).")

@admin_router.message(F.text == "📦 Переглянути товари")
async def admin_view_products(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("📋 Товари (демо):\n1. Товар 1 - 100 грн\n2. Товар 2 - 200 грн")

import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

admin_router = Router()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


# ====== Адмін-панель ======
@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас немає доступу")
        return
    await message.answer("✅ Ви увійшли в адмін-панель\nДоступні команди:\n/add_product\n/delete_product")


# ====== Додавання товару ======
@admin_router.message(Command("add_product"))
async def add_product(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас немає доступу")
        return
    # Тут має бути логіка додавання (поки просто тест)
    await message.answer("📦 Введіть назву нового товару (поки що демо)")


# ====== Видалення товару ======
@admin_router.message(Command("delete_product"))
async def delete_product(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ У вас немає доступу")
        return
    # Тут логіка видалення
    await message.answer("❌ Вкажіть ID товару для видалення (поки що демо)")
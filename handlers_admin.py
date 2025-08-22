from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
import aiosqlite
from config import ADMIN_ID

admin_router = Router()

# Додавання товару
@admin_router.message(Command("add"))
async def cmd_add(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Введи товар у форматі:\nНазва | Опис | Ціна | посилання_на_фото")

@admin_router.message(F.text)
async def add_product(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    if "|" not in message.text:
        return
    try:
        name, description, price, photo = [x.strip() for x in message.text.split("|")]
        async with aiosqlite.connect("shop.db") as db:
            await db.execute("INSERT INTO products (name, description, price, photo) VALUES (?, ?, ?, ?)",
                             (name, description, float(price), photo))
            await db.commit()
        await message.answer("✅ Товар додано!")
    except Exception as e:
        await message.answer(f"❌ Помилка: {e}")

from aiogram import Router, types
from aiogram.filters import Command
from db import add_product

admin_router = Router()

ADMIN_ID = 123456789  # заміни на свій ID

def register_admin_handlers(dp):
    dp.include_router(admin_router)


@admin_router.message(Command("add"))
async def add_product_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Тільки адміністратор може додавати товари.")
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        await message.answer("Формат: /add Назва Ціна Опис")
        return

    name = parts[1]
    try:
        price = float(parts[2])
    except ValueError:
        await message.answer("❌ Ціна має бути числом.")
        return
    description = parts[3]

    await add_product(name=name, description=description, price=price)
    await message.answer(f"✅ Товар {name} доданий!")

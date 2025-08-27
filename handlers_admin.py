from aiogram import Router, types
from aiogram.filters import Command
from db import add_category, add_product

admin_router = Router()

# ⚠️ Тут можна задати ID адміна
ADMIN_ID = 123456789


@admin_router.message(Command("add_category"))
async def cmd_add_category(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ У вас немає прав доступу")
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Використання: /add_category НазваКатегорії")
    name = parts[1]
    await add_category(name)
    await message.answer(f"✅ Категорію '{name}' додано")


@admin_router.message(Command("add_product"))
async def cmd_add_product(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ У вас немає прав доступу")
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
        return await message.answer("Використання: /add_product НазваТовару Ціна ID_Категорії")
    name = parts[1]
    price = float(parts[2])
    category_id = int(parts[3])
    await add_product(name, price, category_id)
    await message.answer(f"✅ Товар '{name}' додано в категорію {category_id}")
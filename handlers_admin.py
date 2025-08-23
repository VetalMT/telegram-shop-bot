import os
from aiogram import Dispatcher, F
from aiogram.types import Message
from keyboards import admin_kb
from db import add_product, delete_product, get_products

ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

# --- Старт адмін-панелі ---
async def admin_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ У вас немає доступу до адмін-панелі.")
    await message.answer("🔧 Ви в адмін-панелі.", reply_markup=admin_kb)
    await message.answer(
        "Команди:\n"
        "• /addprod Назва | Опис | Ціна\n"
        "• /delprod ID\n"
        "• /viewprod"
    )

# --- Додати товар ---
async def add_product_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, data = message.text.split(" ", 1)
        name, description, price = [x.strip() for x in data.split("|")]
        price = float(price)
    except Exception:
        return await message.answer("❌ Формат:\n/addprod Назва | Опис | Ціна")

    product_id = await add_product(name, description, price, None)
    await message.answer(f"✅ Товар '{name}' додано (ID: {product_id})")

# --- Видалити товар ---
async def delete_product_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        product_id = int(message.text.split()[1])
    except Exception:
        return await message.answer("❌ Формат: /delprod ID")

    deleted = await delete_product(product_id)
    if deleted:
        await message.answer(f"🗑 Товар з ID {product_id} видалено.")
    else:
        await message.answer(f"❌ Товар з ID {product_id} не знайдено.")

# --- Перегляд товарів ---
async def view_products_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    products = await get_products()
    if not products:
        return await message.answer("📭 Поки що немає товарів.")

    text = "📦 Товари:\n\n"
    for p in products:
        text += f"🆔 {p[0]} | {p[1]} — {p[3]} грн\n"
    await message.answer(text)

# --- Реєстрація хендлерів ---
def setup_admin_handlers(dp: Dispatcher):
    dp.message.register(admin_start, F.text == "/admin")
    dp.message.register(add_product_cmd, F.text.startswith("/addprod"))
    dp.message.register(delete_product_cmd, F.text.startswith("/delprod"))
    dp.message.register(view_products_cmd, F.text == "/viewprod")

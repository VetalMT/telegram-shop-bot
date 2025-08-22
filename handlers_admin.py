from aiogram import Dispatcher, F
from aiogram.types import Message
from db import add_product
from config import ADMIN_ID

# --- Старт адміна ---
async def admin_start(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Ви не адміністратор.")
    await message.answer("🔧 Ви в адмін-панелі.")

# --- Додати товар ---
async def add_product_cmd(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Ви не адміністратор.")
    try:
        # очікуємо формат: /add Назва|Опис|Ціна|photo_id (photo_id можна залишити пустим)
        parts = message.text.split("|")
        name = parts[0].replace("/add ", "").strip()
        description = parts[1].strip()
        price = float(parts[2].strip())
        photo_id = parts[3].strip() if len(parts) > 3 else None
    except Exception:
        return await message.answer("❌ Використовуйте формат:\n`/add Назва|Опис|Ціна|photo_id`", parse_mode="Markdown")

    product_id = await add_product(name, description, price, photo_id)
    await message.answer(f"✅ Товар додано з ID {product_id}")

# --- Реєстрація хендлерів ---
def setup_admin_handlers(dp: Dispatcher):
    dp.message.register(admin_start, F.text == "/admin")
    dp.message.register(add_product_cmd, F.text.startswith("/add"))

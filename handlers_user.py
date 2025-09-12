import logging
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db import get_products, add_to_cart, get_cart

user_router = Router()
logger = logging.getLogger(__name__)

# ==========================
# 🛍 Головне меню користувача
# ==========================
@user_router.message(F.text == "🛒 Каталог")
async def show_catalog(message: types.Message):
    logger.info("📂 Відкриває каталог user=%s", message.from_user.id)

    try:
        products = await get_products()
        if not products:
            await message.answer("Каталог порожній 😢")
            return

        for p in products:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Додати у кошик", callback_data=f"add:{p['id']}")]
                ]
            )
            await message.answer_photo(
                photo=p["photo"],
                caption=f"<b>{p['name']}</b>\n{p['description']}\n💵 {p['price']} грн",
                reply_markup=kb
            )
    except Exception as e:
        logger.exception("❌ Помилка при show_catalog: %s", e, exc_info=True)
        await message.answer("⚠️ Не вдалося завантажити каталог.")


# ==========================
# 🛒 Кнопка «Додати у кошик»
# ==========================
@user_router.callback_query(F.data.startswith("add:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    logger.info("👉 Спрацював cb_add_to_cart, data=%s", callback.data)
    await callback.answer()  # прибираємо спінер

    try:
        product_id = int(callback.data.split(":", 1)[1])
        logger.info("📦 Додаю товар #%s у кошик для user=%s", product_id, callback.from_user.id)
    except Exception as e:
        logger.exception("❌ Помилка парсингу product_id: %s", callback.data, exc_info=True)
        await callback.message.answer("❗ Невірні дані кнопки.")
        return

    try:
        await add_to_cart(callback.from_user.id, product_id, 1)
        await callback.message.answer("✅ Товар додано у кошик!")
        logger.info("✅ Успішно додано товар %s користувачу %s", product_id, callback.from_user.id)
    except Exception as e:
        logger.exception("❌ Помилка add_to_cart: %s", e, exc_info=True)
        await callback.message.answer("⚠️ Не вдалося додати товар у кошик.")


# ==========================
# 🛒 Кнопка «Переглянути кошик»
# ==========================
@user_router.callback_query(F.data == "cart:open")
async def cb_open_cart(callback: types.CallbackQuery):
    logger.info("👉 Спрацював cb_open_cart для user=%s", callback.from_user.id)
    await callback.answer()

    try:
        cart = await get_cart(callback.from_user.id)
        if not cart:
            await callback.message.answer("🛒 Ваш кошик порожній.")
            return

        text = "🛍 Ваш кошик:\n\n"
        total = 0
        for item in cart:
            text += f"▫️ {item['name']} — {item['quantity']} шт. × {item['price']} грн\n"
            total += item["quantity"] * item["price"]

        text += f"\n💰 Всього: {total} грн"
        await callback.message.answer(text)
        logger.info("✅ Кошик відправлено користувачу %s", callback.from_user.id)
    except Exception as e:
        logger.exception("❌ Помилка show_cart: %s", e, exc_info=True)
        await callback.message.answer("⚠️ Не вдалося завантажити кошик.")


# ==========================
# 🔎 Debug: всі callback-и
# ==========================
@user_router.callback_query()
async def debug_all_callbacks(callback: types.CallbackQuery):
    logger.info("🔎 Отримано callback: %s від user=%s", callback.data, callback.from_user.id)
    await callback.answer()

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


# ==========================
# 🛒 Додавання товару у кошик
# ==========================
@user_router.callback_query(F.data.startswith("add:"))
async def cb_add_to_cart(callback: types.CallbackQuery):
    logger.info("👉 Спрацював cb_add_to_cart, data=%s", callback.data)
    await callback.answer()

    try:
        product_id = int(callback.data.split(":", 1)[1])
        await add_to_cart(callback.from_user.id, product_id, 1)
        await callback.message.answer("✅ Товар додано у кошик!")
        logger.info("✅ Додано товар %s користувачу %s", product_id, callback.from_user.id)
    except Exception as e:
        logger.exception("❌ Помилка у cb_add_to_cart: %s", e)
        await callback.message.answer("⚠️ Не вдалося додати товар у кошик.")


# ==========================
# 🛒 Перегляд кошика
# ==========================
@user_router.message(F.text == "🛍 Кошик")
@user_router.callback_query(F.data == "cart:open")
async def cb_open_cart(event: types.Message | types.CallbackQuery):
    user_id = event.from_user.id
    logger.info("👉 Спрацював cb_open_cart для user=%s", user_id)

    if isinstance(event, types.CallbackQuery):
        await event.answer()
        target = event.message
    else:
        target = event

    cart = await get_cart(user_id)
    if not cart:
        await target.answer("🛒 Ваш кошик порожній.")
        return

    text = "🛍 Ваш кошик:\n\n"
    total = 0
    for item in cart:
        text += f"▫️ {item['name']} — {item['quantity']} шт. × {item['price']} грн\n"
        total += item["quantity"] * item["price"]

    text += f"\n💰 Всього: {total} грн"
    await target.answer(text)


# ==========================
# 🔎 Debug: всі callback-и
# ==========================
@user_router.callback_query()
async def debug_all_callbacks(callback: types.CallbackQuery):
    logger.info("🔎 Отримано callback: %s від user=%s", callback.data, callback.from_user.id)
    await callback.answer("⚠️ Кнопка ще не підключена.")

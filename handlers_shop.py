from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import products, carts

router = Router()

# --- Каталог ---
@router.message(F.text == "🛍 Каталог")
async def shop_catalog(message: Message):
    if not products:
        return await message.answer("📭 Немає товарів.")
    for p in products:
        kb = InlineKeyboardBuilder()
        kb.button(text="🛒 Додати в кошик", callback_data=f"addcart:{p['id']}")
        kb.adjust(1)
        await message.answer_photo(
            photo=p["photo"],
            caption=f"<b>{p['name']}</b>\n{p['description']}\n💰 {p['price']} грн",
            reply_markup=kb.as_markup()
        )

# --- Додати товар у кошик ---
@router.callback_query(F.data.startswith("addcart:"))
async def add_to_cart(cb: CallbackQuery):
    product_id = int(cb.data.split(":")[1])
    user_id = cb.from_user.id
    carts.setdefault(user_id, [])
    carts[user_id].append(product_id)
    await cb.answer("✅ Додано в кошик!", show_alert=False)

# --- Переглянути кошик ---
@router.message(F.text == "🛒 Кошик")
async def view_cart(message: Message):
    user_id = message.from_user.id
    cart = carts.get(user_id, [])
    if not cart:
        return await message.answer("🛒 Ваш кошик порожній.")
    total = 0
    text = "🛍 Ваш кошик:\n\n"
    for pid in cart:
        p = next((x for x in products if x["id"] == pid), None)
        if p:
            text += f"- {p['name']} | {p['price']} грн\n"
            total += p["price"]
    text += f"\n💰 Всього: {total} грн"
    await message.answer(text)

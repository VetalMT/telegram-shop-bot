import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN
from db import Database

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()

# ------------------- START -------------------
@dp.message(commands=["start"])
async def start(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.first_name)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Каталог"), KeyboardButton("Кошик"))
    if message.from_user.id == 123456789:  # 👈 сюди встав свій ID для адміна
        kb.add(KeyboardButton("➕ Додати товар"), KeyboardButton("🗑 Видалити товар"))
        kb.add(KeyboardButton("📦 Переглянути товари"))
    await message.answer("Вітаю у магазині!", reply_markup=kb)

# ------------------- ADMIN -------------------
@dp.message(lambda msg: msg.text == "➕ Додати товар")
async def add_product(message: types.Message):
    await message.answer("Введи назву товару:")
    # (Тут треба FSM щоб по черзі питати назву, опис, ціну, фото 👉 можу додати окремо)

@dp.message(lambda msg: msg.text == "📦 Переглянути товари")
async def view_products(message: types.Message):
    products = await db.get_products()
    if not products:
        await message.answer("Немає товарів.")
        return
    text = "📦 Список товарів:\n\n"
    for p in products:
        text += f"ID: {p['id']}\nНазва: {p['name']}\nЦіна: {p['price']} грн\n\n"
    await message.answer(text)

@dp.message(lambda msg: msg.text == "🗑 Видалити товар")
async def delete_product(message: types.Message):
    await message.answer("Введи ID товару для видалення:")

# ------------------- BUYER -------------------
@dp.message(lambda msg: msg.text == "Каталог")
async def catalog(message: types.Message):
    products = await db.get_products()
    if not products:
        await message.answer("Каталог пустий.")
        return
    for p in products:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("➕ Додати у кошик", callback_data=f"add_{p['id']}"))
        await message.answer_photo(p["photo"], caption=f"{p['name']}\n{p['description']}\n💰 {p['price']} грн", reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await db.add_to_cart(callback.from_user.id, product_id)
    await callback.answer("Додано у кошик ✅")

@dp.message(lambda msg: msg.text == "Кошик")
async def view_cart(message: types.Message):
    cart = await db.get_cart(message.from_user.id)
    if not cart:
        await message.answer("Кошик пустий.")
        return
    text = "🛒 Ваш кошик:\n\n"
    kb = types.InlineKeyboardMarkup()
    for item in cart:
        text += f"{item['name']} - {item['price']} грн\n"
        kb.add(types.InlineKeyboardButton(f"❌ Видалити {item['name']}", callback_data=f"del_{item['id']}"))
    kb.add(types.InlineKeyboardButton("✅ Оформити замовлення", callback_data="checkout"))
    await message.answer(text, reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("del_"))
async def remove_from_cart(callback: types.CallbackQuery):
    cart_id = int(callback.data.split("_")[1])
    await db.remove_from_cart(cart_id)
    await callback.answer("Видалено ✅")

# ------------------- MAIN -------------------
async def main():
    await db.connect()
    await db.create_tables()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

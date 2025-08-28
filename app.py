import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from db import init_db, add_product, delete_product, get_products

logging.basicConfig(level=logging.INFO)

TOKEN = "ТВОЙ_ТОКЕН_ТУТ"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- Головне меню ---
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Додати товар")],
        [KeyboardButton(text="❌ Видалити товар")],
        [KeyboardButton(text="📦 Переглянути товари")]
    ],
    resize_keyboard=True
)

# --- Старт ---
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Вітаю у магазині! Виберіть дію:", reply_markup=main_kb)

# --- Додати товар ---
@dp.message(lambda m: m.text == "➕ Додати товар")
async def ask_name(message: types.Message):
    await message.answer("Введіть назву товару:")
    dp.workflow_data[message.from_user.id] = {"state": "add_name"}

@dp.message(lambda m: dp.workflow_data.get(m.from_user.id, {}).get("state") == "add_name")
async def ask_desc(message: types.Message):
    dp.workflow_data[message.from_user.id]["name"] = message.text
    dp.workflow_data[message.from_user.id]["state"] = "add_desc"
    await message.answer("Введіть опис товару:")

@dp.message(lambda m: dp.workflow_data.get(m.from_user.id, {}).get("state") == "add_desc")
async def ask_price(message: types.Message):
    dp.workflow_data[message.from_user.id]["description"] = message.text
    dp.workflow_data[message.from_user.id]["state"] = "add_price"
    await message.answer("Введіть ціну товару:")

@dp.message(lambda m: dp.workflow_data.get(m.from_user.id, {}).get("state") == "add_price")
async def save_product(message: types.Message):
    try:
        price = float(message.text)
        data = dp.workflow_data[message.from_user.id]
        await add_product(data["name"], data["description"], price)
        await message.answer("✅ Товар додано!", reply_markup=main_kb)
        dp.workflow_data.pop(message.from_user.id, None)
    except ValueError:
        await message.answer("❌ Ціна має бути числом. Спробуйте ще раз.")

# --- Видалити товар ---
@dp.message(lambda m: m.text == "❌ Видалити товар")
async def choose_delete(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("⚠️ Немає товарів для видалення.")
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"{p['id']}. {p['name']}")] for p in products],
        resize_keyboard=True
    )
    dp.workflow_data[message.from_user.id] = {"state": "delete"}
    await message.answer("Виберіть товар для видалення:", reply_markup=kb)

@dp.message(lambda m: dp.workflow_data.get(m.from_user.id, {}).get("state") == "delete")
async def do_delete(message: types.Message):
    try:
        product_id = int(message.text.split(".")[0])
        await delete_product(product_id)
        await message.answer("✅ Товар видалено.", reply_markup=main_kb)
    except Exception:
        await message.answer("❌ Невірний вибір.", reply_markup=main_kb)
    dp.workflow_data.pop(message.from_user.id, None)

# --- Переглянути товари ---
@dp.message(lambda m: m.text == "📦 Переглянути товари")
async def view_products(message: types.Message):
    products = await get_products()
    if not products:
        await message.answer("⚠️ Немає товарів.")
        return
    text = "\n\n".join([f"📌 {p['id']}. {p['name']}\n📝 {p['description']}\n💰 {p['price']} грн" for p in products])
    await message.answer(text)

# --- Все інше ---
@dp.message()
async def unknown(message: types.Message):
    await message.answer("❓ Не зрозумів... Виберіть категорію з меню.", reply_markup=main_kb)

# --- Запуск ---
async def main():
    await init_db()
    dp.workflow_data = {}
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

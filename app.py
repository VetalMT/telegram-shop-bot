import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from fastapi import FastAPI, Request
import uvicorn
import os

# -------------------
# Налаштування
# -------------------
TOKEN = os.getenv("BOT_TOKEN")  # 🔑 твій токен сюди
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # 🔗 твій домен + /webhook

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

# -------------------
# Дані магазину
# -------------------
PRODUCTS = {
    "📱 Телефони": ["iPhone 15", "Samsung S23", "Xiaomi 13"],
    "💻 Ноутбуки": ["MacBook Pro", "Dell XPS", "Lenovo ThinkPad"]
}
CART = {}  # {user_id: [items]}

# -------------------
# Адмін
# -------------------
ADMIN_IDS = [123456789]  # 👉 заміни на свій Telegram ID

# -------------------
# Хендлери
# -------------------
@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📱 Телефони"), types.KeyboardButton(text="💻 Ноутбуки")],
            [types.KeyboardButton(text="🛒 Корзина")]
        ],
        resize_keyboard=True
    )
    await message.answer("Вітаю у нашому магазині! Оберіть категорію:", reply_markup=kb)

@dp.message(F.text.in_(PRODUCTS.keys()))
async def show_products(message: Message):
    category = message.text
    kb = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=p)] for p in PRODUCTS[category]] + [[types.KeyboardButton(text="⬅️ Назад")]],
        resize_keyboard=True
    )
    await message.answer(f"Оберіть товар із категорії {category}:", reply_markup=kb)

@dp.message(F.text.in_(sum(PRODUCTS.values(), [])))
async def add_to_cart(message: Message):
    user_id = message.from_user.id
    CART.setdefault(user_id, []).append(message.text)
    await message.answer(f"✅ {message.text} додано у корзину!")

@dp.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    user_id = message.from_user.id
    items = CART.get(user_id, [])
    if not items:
        await message.answer("Ваша корзина порожня 🛍️")
        return
    text = "🛒 Ваша корзина:\n- " + "\n- ".join(items)
    await message.answer(text)

@dp.message(F.text == "⬅️ Назад")
async def back_to_menu(message: Message):
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📱 Телефони"), types.KeyboardButton(text="💻 Ноутбуки")],
            [types.KeyboardButton(text="🛒 Корзина")]
        ],
        resize_keyboard=True
    )
    await message.answer("⬅️ Ви повернулися у головне меню.", reply_markup=kb)

# -------------------
# Адмін-панель
# -------------------
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔ У вас немає доступу до адмін-панелі.")
        return

    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📦 Замовлення")],
            [types.KeyboardButton(text="➕ Додати товар")],
            [types.KeyboardButton(text="⬅️ Вийти")]
        ],
        resize_keyboard=True
    )
    await message.answer("🔐 Адмін-панель:", reply_markup=kb)

@dp.message(F.text == "📦 Замовлення")
async def show_orders(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    if not CART:
        await message.answer("Поки що замовлень немає 📭")
        return

    text = "📦 Усі замовлення:\n\n"
    for uid, items in CART.items():
        text += f"👤 {uid}:\n - " + "\n - ".join(items) + "\n\n"

    await message.answer(text)

@dp.message(F.text == "➕ Додати товар")
async def add_product_admin(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("✏️ Введіть новий товар у форматі: Категорія | Назва")
    await state.set_state("add_product")

@dp.message(F.text, state="add_product")
async def save_new_product(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        category, product = message.text.split("|")
        category, product = category.strip(), product.strip()
        if category not in PRODUCTS:
            PRODUCTS[category] = []
        PRODUCTS[category].append(product)
        await message.answer(f"✅ Товар '{product}' додано у категорію '{category}'!")
    except:
        await message.answer("❌ Формат неправильний. Використовуйте: Категорія | Назва")
    await state.clear()

@dp.message(F.text == "⬅️ Вийти")
async def exit_admin(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await start_handler(message, None)

# -------------------
# Webhook
# -------------------
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8080)))

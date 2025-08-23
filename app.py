import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start_webhook
from db import init_db, add_product, delete_product, get_all_products

# Логування
logging.basicConfig(level=logging.INFO)

# Конфіг
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))  # твій Telegram ID
APP_URL = os.getenv("APP_URL")  # Render URL
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 5000))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Клавіатури ---
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("🛒 Магазин"))

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add("➕ Додати товар", "❌ Видалити товар")
admin_menu.add("📋 Переглянути товари")
admin_menu.add("⬅️ Назад")

# --- Старт ---
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привіт, адміністраторе! 👑", reply_markup=admin_menu)
    else:
        await message.answer("Вітаю! Це онлайн-магазин 🛒", reply_markup=main_menu)

# --- Адмін-панель ---
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "📋 Переглянути товари")
async def view_products(message: types.Message):
    products = get_all_products()
    if not products:
        await message.answer("Немає жодного товару.")
        return
    text = "📋 Список товарів:\n\n"
    for p in products:
        text += f"🆔 {p[0]} | {p[1]} - {p[2]} грн\n"
    await message.answer(text)

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "➕ Додати товар")
async def add_product_start(message: types.Message):
    await message.answer("Введи назву товару:")
    dp.register_message_handler(process_product_name, state="*")

async def process_product_name(message: types.Message):
    dp.product_name = message.text
    await message.answer("Введи ціну товару (числом):")
    dp.register_message_handler(process_product_price, state="*")

async def process_product_price(message: types.Message):
    try:
        price = float(message.text)
        add_product(dp.product_name, price)
        await message.answer(f"✅ Товар '{dp.product_name}' додано за {price} грн", reply_markup=admin_menu)
    except ValueError:
        await message.answer("❌ Ціна має бути числом. Спробуй ще раз.")

@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "❌ Видалити товар")
async def delete_product_start(message: types.Message):
    products = get_all_products()
    if not products:
        await message.answer("Немає товарів для видалення.")
        return
    kb = InlineKeyboardMarkup()
    for p in products:
        kb.add(InlineKeyboardButton(f"{p[1]} ({p[2]} грн)", callback_data=f"del_{p[0]}"))
    await message.answer("Оберіть товар для видалення:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("del_"))
async def process_delete(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    delete_product(product_id)
    await callback.message.edit_text(f"✅ Товар ID {product_id} видалено.")

# --- Магазин (звичайні користувачі) ---
@dp.message_handler(lambda m: m.text == "🛒 Магазин")
async def shop_menu(message: types.Message):
    products = get_all_products()
    if not products:
        await message.answer("Магазин порожній 😢")
        return
    kb = InlineKeyboardMarkup()
    for p in products:
        kb.add(InlineKeyboardButton(f"{p[1]} - {p[2]} грн", callback_data=f"buy_{p[0]}"))
    await message.answer("🛒 Товари:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    products = get_all_products()
    product = next((p for p in products if p[0] == product_id), None)
    if product:
        await callback.message.answer(f"✅ Ви купили {product[1]} за {product[2]} грн")
    else:
        await callback.message.answer("❌ Товар не знайдено")

# --- Webhook ---
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    init_db()

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )

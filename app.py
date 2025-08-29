import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI, Request
from aiogram.fsm.storage.memory import MemoryStorage

# --- Логування ---
logging.basicConfig(level=logging.INFO)

# --- Токен ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ У .env немає BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# --- FSM ---
class OrderForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()

# --- FastAPI ---
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = bot.session.json_loads(data)
    await dp.feed_webhook_update(bot, update)
    return {"ok": True}

@app.on_event("startup")
async def on_startup():
    webhook_url = os.getenv("RENDER_EXTERNAL_URL") + "/webhook"
    await bot.set_webhook(webhook_url)
    logging.info(f"✅ Webhook встановлено: {webhook_url}")

# --- Клавіатури ---
def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 Категорії", callback_data="categories")
    kb.button(text="ℹ️ Про нас", callback_data="about")
    kb.adjust(1)
    return kb.as_markup()

def categories_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📱 Телефони", callback_data="cat_phones")
    kb.button(text="💻 Ноутбуки", callback_data="cat_laptops")
    kb.button(text="⬅️ Назад", callback_data="back_main")
    kb.adjust(1)
    return kb.as_markup()

def products_kb(category: str):
    kb = InlineKeyboardBuilder()
    if category == "phones":
        kb.button(text="iPhone 15", callback_data="prod_iphone15")
        kb.button(text="Samsung S24", callback_data="prod_s24")
    elif category == "laptops":
        kb.button(text="MacBook Pro", callback_data="prod_macbook")
        kb.button(text="Asus ROG", callback_data="prod_asus")
    kb.button(text="⬅️ Назад", callback_data="categories")
    kb.adjust(1)
    return kb.as_markup()

def confirm_order_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Підтвердити замовлення", callback_data="confirm_order")
    kb.button(text="❌ Скасувати", callback_data="cancel_order")
    kb.adjust(1)
    return kb.as_markup()

# --- Хендлери ---
@dp.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer("👋 Вітаю у магазині! Обери дію:", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    await callback.message.edit_text("🔝 Головне меню:", reply_markup=main_menu_kb())

@dp.callback_query(F.data == "categories")
async def show_categories(callback: CallbackQuery):
    await callback.message.edit_text("📂 Оберіть категорію:", reply_markup=categories_kb())

@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.edit_text("ℹ️ Ми продаємо техніку за найкращими цінами!", reply_markup=main_menu_kb())

# --- Товари ---
@dp.callback_query(F.data == "cat_phones")
async def phones(callback: CallbackQuery):
    await callback.message.edit_text("📱 Телефони:", reply_markup=products_kb("phones"))

@dp.callback_query(F.data == "cat_laptops")
async def laptops(callback: CallbackQuery):
    await callback.message.edit_text("💻 Ноутбуки:", reply_markup=products_kb("laptops"))

@dp.callback_query(F.data.startswith("prod_"))
async def select_product(callback: CallbackQuery, state: FSMContext):
    product_map = {
        "prod_iphone15": "iPhone 15",
        "prod_s24": "Samsung S24",
        "prod_macbook": "MacBook Pro",
        "prod_asus": "Asus ROG",
    }
    product = product_map.get(callback.data, "Невідомий товар")
    await state.update_data(product=product)
    await callback.message.edit_text(
        f"🛍 Ви обрали: <b>{product}</b>\n\nВведіть ваше ім'я:",
        parse_mode="HTML"
    )
    await state.set_state(OrderForm.waiting_for_name)

# --- Збереження імені ---
@dp.message(StateFilter(OrderForm.waiting_for_name))
async def save_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📍 Введіть адресу доставки:")
    await state.set_state(OrderForm.waiting_for_address)

# --- Збереження адреси ---
@dp.message(StateFilter(OrderForm.waiting_for_address))
async def save_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()

    text = (
        f"📝 Ваше замовлення:\n\n"
        f"Товар: <b>{data['product']}</b>\n"
        f"Ім'я: <b>{data['name']}</b>\n"
        f"Адреса: <b>{data['address']}</b>\n\n"
        f"Підтвердити?"
    )
    await message.answer(text, reply_markup=confirm_order_kb(), parse_mode="HTML")

# --- Підтвердження ---
@dp.callback_query(F.data == "confirm_order")
async def confirm(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("✅ Дякуємо за замовлення! Ми з вами зв'яжемося 📦")
    await state.clear()

@dp.callback_query(F.data == "cancel_order")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Замовлення скасовано.", reply_markup=main_menu_kb())
    await state.clear()

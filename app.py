import os
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio

# ==========================
# Налаштування
# ==========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Не вказано BOT_TOKEN у змінних оточення!")

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

app = FastAPI()


# ==========================
# Стан машини (FSM)
# ==========================
class OrderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_product = State()


# ==========================
# Клавіатури
# ==========================
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🛒 Замовити товар"))
main_kb.add(KeyboardButton("ℹ️ Про нас"))


# ==========================
# Обробники
# ==========================
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("Вітаємо у нашому магазині! Оберіть дію:", reply_markup=main_kb)


@dp.message_handler(lambda m: m.text == "🛒 Замовити товар")
async def order_product(message: types.Message):
    await message.answer("Введіть ваше ім’я:")
    await OrderState.waiting_for_name.set()


@dp.message_handler(state=OrderState.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введіть ваш номер телефону:")
    await OrderState.waiting_for_phone.set()


@dp.message_handler(state=OrderState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Який товар ви хочете замовити?")
    await OrderState.waiting_for_product.set()


@dp.message_handler(state=OrderState.waiting_for_product)
async def process_product(message: types.Message, state: FSMContext):
    await state.update_data(product=message.text)
    data = await state.get_data()

    summary = (
        f"✅ Замовлення прийняте!\n\n"
        f"👤 Ім’я: {data['name']}\n"
        f"📞 Телефон: {data['phone']}\n"
        f"📦 Товар: {data['product']}"
    )

    await message.answer(summary, reply_markup=main_kb)
    await state.finish()


@dp.message_handler(lambda m: m.text == "ℹ️ Про нас")
async def about(message: types.Message):
    await message.answer("Ми — тестовий онлайн-магазин 🚀")


# ==========================
# FastAPI маршрути
# ==========================
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook встановлено: {WEBHOOK_URL}")


@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()
    print("Бот зупинений.")


@app.post("/webhook/{token}")
async def webhook_handler(token: str, request: Request):
    if token != BOT_TOKEN:
        return {"error": "Invalid token"}

    update = await request.json()
    telegram_update = types.Update.to_object(update)
    await dp.process_update(telegram_update)
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"status": "Bot is running"}


# ==========================
# Запуск локально (не для Render)
# ==========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

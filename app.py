import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiogram.types.webhook import Webhook
from aiogram.dispatcher.webhook.aiohttp_server import SimpleRequestHandler
import pdfkit  # для генерації PDF

# ---------- Налаштування логів ----------
logging.basicConfig(level=logging.INFO)

# ---------- Конфіг ----------
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # https://your-app.onrender.com/webhook
PORT = int(os.getenv("PORT", 10000))

# ---------- Ініціалізація бота ----------
bot = Bot(
    token=BOT_TOKEN,
    session=AiohttpSession(),
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# ---------- FSM ----------
class OrderStates(StatesGroup):
    choosing_product = State()
    entering_name = State()
    entering_address = State()
    confirm_order = State()

# ---------- Старт команди ----------
@dp.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купити товар", callback_data="buy")]
    ])
    await message.answer("Вітаю! Обери дію:", reply_markup=kb)

# ---------- Кнопки ----------
@dp.callback_query(F.data == "buy")
async def buy_callback(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Введіть назву товару, який хочете замовити:")
    await state.set_state(OrderStates.choosing_product)

@dp.message(OrderStates.choosing_product)
async def choose_product(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    await message.answer("Введіть своє ім'я:")
    await state.set_state(OrderStates.entering_name)

@dp.message(OrderStates.entering_name)
async def enter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введіть адресу доставки:")
    await state.set_state(OrderStates.entering_address)

@dp.message(OrderStates.entering_address)
async def enter_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    await message.answer(
        f"Підтвердіть замовлення:\n\n"
        f"Товар: {data['product']}\n"
        f"Ім'я: {data['name']}\n"
        f"Адреса: {data['address']}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("✅ Підтвердити", callback_data="confirm")],
            [InlineKeyboardButton("❌ Відмінити", callback_data="cancel")]
        ])
    )
    await state.set_state(OrderStates.confirm_order)

@dp.callback_query(F.data == "confirm", state=OrderStates.confirm_order)
async def confirm_order(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    pdf_filename = f"{data['name']}_order.pdf"

    # ---------- Генерація PDF ----------
    html_content = f"""
    <h1>Замовлення</h1>
    <p><b>Товар:</b> {data['product']}</p>
    <p><b>Ім'я:</b> {data['name']}</p>
    <p><b>Адреса:</b> {data['address']}</p>
    """
    pdfkit.from_string(html_content, pdf_filename)

    await call.message.answer_document(open(pdf_filename, "rb"), caption="Ваш PDF-квиток")
    await call.message.answer("Дякуємо за замовлення!")
    await state.clear()

@dp.callback_query(F.data == "cancel", state=OrderStates.confirm_order)
async def cancel_order(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Замовлення скасовано.")
    await state.clear()

# ---------- FastAPI для Webhook ----------
app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

@app.post("/webhook")
async def webhook_handler(request: Request):
    data = await request.json()
    update = Webhook(**data)
    await dp.feed_update(update)
    return JSONResponse(content={"ok": True})

# ---------- Основний запуск для локальної перевірки ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

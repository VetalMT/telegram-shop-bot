import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# ================== CONFIG ==================
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("❌ API_TOKEN не заданий у змінних середовища!")

WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== BOT ==================
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================== STATES ==================
class OrderStates(StatesGroup):
    choosing_category = State()
    choosing_product = State()
    confirming = State()

# ================== HANDLERS ==================
@dp.message(commands=["start"])
async def start_handler(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🛒 Товари")]],
        resize_keyboard=True
    )
    await message.answer("Привіт! 👋 Обери дію:", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_category)


@dp.message(lambda m: m.text == "🛒 Товари")
async def show_products(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🍏 Яблука"), types.KeyboardButton(text="🍌 Банани")],
            [types.KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Ось доступні товари:", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_product)


@dp.message(lambda m: m.text in ["🍏 Яблука", "🍌 Банани"])
async def choose_product(message: types.Message, state: FSMContext):
    await state.update_data(product=message.text)
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="✅ Підтвердити"), types.KeyboardButton(text="❌ Скасувати")]
        ],
        resize_keyboard=True
    )
    await message.answer(f"Ти вибрав {message.text}. Підтверджуєш покупку?", reply_markup=keyboard)
    await state.set_state(OrderStates.confirming)


@dp.message(lambda m: m.text == "✅ Підтвердити")
async def confirm_order(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(f"✅ Замовлення підтверджено: {data.get('product')}", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()


@dp.message(lambda m: m.text in ["❌ Скасувати", "⬅️ Назад"])
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="🛒 Товари")]],
        resize_keyboard=True
    )
    await message.answer("❌ Дію скасовано. Обери нову:", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_category)

# ================== AIOHTTP APP ==================
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook set to {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await bot.session.close()

async def handle_webhook(request: web.Request):
    try:
        data = await request.json()
        update = types.Update(**data)
        await dp.feed_update(bot, update)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
    return web.Response(text="ok")

# 🔹 Кореневий маршрут для пінгів (keep alive)
async def handle_root(request: web.Request):
    return web.json_response({"status": "ok"})

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.router.add_get("/", handle_root)  # <-- тут ключове
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
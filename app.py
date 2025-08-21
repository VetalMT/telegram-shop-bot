
import os
import logging
from fastapi import FastAPI, Request, HTTPException
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from keyboards import shop_kb, admin_kb
from config import BOT_TOKEN, ADMIN_ID

# ---------- Logging ----------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("tg-shop")

# ---------- Bot / Dispatcher ----------
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# ---------- FastAPI app ----------
app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "supersecret")         # set in Render env
WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"
BASE_URL = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_BASE_URL")  # set WEBHOOK_BASE_URL if needed

@app.on_event("startup")
async def on_startup():
    if BASE_URL:
        url = BASE_URL.rstrip("/") + WEBHOOK_PATH
        await bot.set_webhook(url)
        log.info(f"Webhook set to: {url}")
    else:
        log.warning("No BASE_URL provided. Set env WEBHOOK_BASE_URL to your service URL on Render.")

@app.on_event("shutdown")
async def on_shutdown():
    try:
        await bot.delete_webhook()
        log.info("Webhook deleted")
    except Exception as e:
        log.warning(f"delete_webhook error: {e}")

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}

# ---------- Handlers ----------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Привіт, адміністратор! 👑", reply_markup=admin_kb)
    else:
        await message.answer("Вітаємо у нашому магазині 🛒", reply_markup=shop_kb)

# Add your next handlers here (товари/корзина/адмін-дії)

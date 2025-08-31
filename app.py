import os
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncpg
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
PORT = int(os.environ.get("PORT", 8000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад: https://твій-домен.onrender.com/webhook/<BOT_TOKEN>

app = FastAPI()
telegram_app = ApplicationBuilder().token(BOT_TOKEN).build()
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"


# --- PostgreSQL: збереження користувача ---
async def save_user(telegram_id: int, username: str | None):
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username TEXT
        );
    """)
    await conn.execute("""
        INSERT INTO users (telegram_id, username)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id) DO NOTHING;
    """, telegram_id, username)
    await conn.close()


# --- Команди бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id, user.username)
    await update.message.reply_text(f"Привіт, {user.first_name}! Ласкаво просимо до нашого магазину.")


telegram_app.add_handler(CommandHandler("start", start))


# --- Webhook endpoint ---
@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.update_queue.put(update)
    return {"ok": True}


# --- Запуск бота у фоновому завданні ---
@app.on_event("startup")
async def on_startup():
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.bot.set_webhook(WEBHOOK_URL)
    print("Бот запущено на Webhook!")


@app.on_event("shutdown")
async def on_shutdown():
    await telegram_app.stop()
    await telegram_app.shutdown()

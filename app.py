import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncpg
from dotenv import load_dotenv

load_dotenv()

# --- Змінні середовища ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Напр.: https://твій-домен.onrender.com/

logging.basicConfig(level=logging.INFO)


# --- Команди бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await save_user(user.id, user.username)
    await update.message.reply_text(
        f"Привіт, {user.first_name}! Ласкаво просимо до нашого магазину."
    )


# --- PostgreSQL: збереження користувача ---
async def save_user(telegram_id: int, username: str | None):
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE,
            username TEXT
        );
        """
    )
    await conn.execute(
        """
        INSERT INTO users (telegram_id, username)
        VALUES ($1, $2)
        ON CONFLICT (telegram_id) DO NOTHING;
        """,
        telegram_id, username
    )
    await conn.close()


# --- Ініціалізація бота ---
async def main():
    # Створюємо Application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Додаємо команди
    app.add_handler(CommandHandler("start", start))

    # --- Webhook для Render ---
    await app.bot.set_webhook(WEBHOOK_URL)
    print("Бот запущено на Webhook!")

    # Для Render запускаємо додаток без run_polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling()  # optional для dev
    await app.updater.idle()


# --- Запуск ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

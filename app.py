import asyncio
from aiogram import Bot, Dispatcher
from config import TOKEN
from handlers_admin import admin_router
from handlers_shop import shop_router
import aiosqlite

async def on_startup():
    # створюємо БД, якщо немає
    async with aiosqlite.connect("shop.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                photo TEXT
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER DEFAULT 1
            )
        """)
        await db.commit()

async def main():
    await on_startup()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(admin_router)
    dp.include_router(shop_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

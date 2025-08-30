import asyncio
from aiogram import Bot, Dispatcher
import logging
from config import BOT_TOKEN
import db
import handlers_admin, handlers_user

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    pool = await db.create_pool()
    await db.init_db(pool)

    dp.include_router(handlers_admin.router)
    dp.include_router(handlers_user.router)

    # Проброс pool у всі хендлери
    async def pool_middleware(handler, event, data):
        data["pool"] = pool
        return await handler(event, data)
    dp.message.middleware(pool_middleware)
    dp.callback_query.middleware(pool_middleware)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

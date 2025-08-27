from aiogram import Router, types
from aiogram.filters import Command

user_router = Router()

@user_router.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("👋 Вітаю! Це тестовий магазин. Використовуйте /admin для входу в адмін-панель.")


# fallback для незрозумілих повідомлень
@user_router.message()
async def fallback(message: types.Message):
    await message.answer("❓ Не зрозумів... Виберіть категорію з меню")
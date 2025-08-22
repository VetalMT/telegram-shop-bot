from aiogram import Dispatcher, F
from aiogram.types import Message


# Приклад команди /admin
async def admin_start(message: Message):
    await message.answer("🔧 Ви в адмін-панелі.")


# Реєстрація адмінських хендлерів
def setup_admin_handlers(dp: Dispatcher):
    dp.message.register(admin_start, F.text == "/admin")

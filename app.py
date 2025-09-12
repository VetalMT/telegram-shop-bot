import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.client.default import DefaultBotProperties
from config import TOKEN, WEBHOOK_URL, WEBAPP_HOST, WEBAPP_PORT

# ---------------------------
# 🔧 Логування
# ---------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------
# 🔧 Ініціалізація бота
# ---------------------------
bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")  # ✅ новий синтаксис Aiogram 3.7
)
dp = Dispatcher()

# ---------------------------
# 📌 Handlers
# ---------------------------
@dp.message(commands=["start"])
async def start_cmd(message: types.Message):
    await message.answer("👋 Привіт! Бот магазину працює ✅")

@dp.message(commands=["help"])
async def help_cmd(message: types.Message):
    await message.answer("ℹ️ Доступні команди:\n/start - початок\n/help - допомога")

@dp.message()
async def echo_handler(message: types.Message):
    await message.answer(f"📩 Ти написав: {message.text}")

# ---------------------------
# 📌 Webhook запуск
# ---------------------------
async def on_startup(app: web.Application):
    logger.info("🚀 on_startup: ініціалізація...")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"✅ Webhook встановлено: {WEBHOOK_URL}")

async def on_shutdown(app: web.Application):
    logger.info("🛑 Вимикаюсь...")
    await bot.delete_webhook()
    await bot.session.close()

def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # ✅ Прив'язуємо webhook dispatcher
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{TOKEN}")
    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    main()

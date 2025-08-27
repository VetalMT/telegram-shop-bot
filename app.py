import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

from db import init_db, add_product, get_products, get_product

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==== КНОПКИ ====
def products_keyboard(products):
    kb = InlineKeyboardMarkup()
    for product in products:
        kb.add(
            InlineKeyboardButton(
                text=f"{product['name']} - {product['price']}₴",
                callback_data=f"product_{product['id']}"
            )
        )
    return kb


# ==== ХЕНДЛЕРИ ====
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привіт 👋 Це магазин!\nВведи /products щоб подивитись товари.")


@dp.message(Command("products"))
async def cmd_products(message: Message):
    products = get_products()
    if not products:
        await message.answer("Немає товарів 😔")
    else:
        await message.answer("Наші товари:", reply_markup=products_keyboard(products))


@dp.callback_query()
async def callbacks(callback: CallbackQuery):
    if callback.data.startswith("product_"):
        product_id = int(callback.data.split("_")[1])
        product = get_product(product_id)

        if product:
            text = f"🛒 <b>{product['name']}</b>\n💵 Ціна: {product['price']}₴\n\n{product['description'] or ''}"
            if product["image_url"]:
                await bot.send_photo(callback.from_user.id, photo=product["image_url"], caption=text, parse_mode="HTML")
            else:
                await bot.send_message(callback.from_user.id, text, parse_mode="HTML")
        else:
            await bot.send_message(callback.from_user.id, "Товар не знайдено 😔")

        await callback.answer()


# ==== СТАРТ ====
async def main():
    init_db()  # створює таблиці, якщо ще нема
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode

from db import add_product, get_products, delete_product, count_products
from config import ADMIN_ID
from keyboards import admin_kb

# FSM
class AddProductFSM(StatesGroup):
    name = State()
    description = State()
    price = State()
    photo = State()

def register_admin(dp: Dispatcher):
    @dp.message_handler(commands=["admin"])
    async def cmd_admin(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            await message.answer("⛔ У вас немає прав адміністратора.")
            return
        await message.answer("⚙️ Адмін-панель. Оберіть дію:", reply_markup=admin_kb())

    @dp.message_handler(Text(equals="➕ Додати товар"))
    async def admin_add_product_start(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return
        await AddProductFSM.name.set()
        await message.answer("📝 Введіть назву товару:")

    @dp.message_handler(state=AddProductFSM.name)
    async def admin_add_product_name(message: types.Message, state: FSMContext):
        await state.update_data(name=message.text.strip())
        await AddProductFSM.next()
        await message.answer("✍️ Введіть опис товару:")

    @dp.message_handler(state=AddProductFSM.description)
    async def admin_add_product_description(message: types.Message, state: FSMContext):
        await state.update_data(description=message.text.strip())
        await AddProductFSM.next()
        await message.answer("💵 Введіть ціну (число, напр. 199.99):")

    @dp.message_handler(state=AddProductFSM.price)
    async def admin_add_product_price(message: types.Message, state: FSMContext):
        text = message.text.replace(",", ".").strip()
        try:
            price = float(text)
        except ValueError:
            await message.answer("❗ Невірний формат. Введіть число, напр. 199.99")
            return
        await state.update_data(price=price)
        await AddProductFSM.next()
        await message.answer("📸 Надішліть фото товару або введіть /skip щоб пропустити.")

    @dp.message_handler(commands=["skip"], state=AddProductFSM.photo)
    async def admin_add_product_skip_photo(message: types.Message, state: FSMContext):
        await state.update_data(photo_id=None)
        data = await state.get_data()
        pid = await add_product(data["name"], data["description"], data["price"], data.get("photo_id"))
        await state.finish()
        await message.answer(f"✅ Товар додано! (ID: {pid})", reply_markup=admin_kb())

    @dp.message_handler(content_types=types.ContentType.PHOTO, state=AddProductFSM.photo)
    async def admin_add_product_photo(message: types.Message, state: FSMContext):
        photo_id = message.photo[-1].file_id
        await state.update_data(photo_id=photo_id)
        data = await state.get_data()
        pid = await add_product(data["name"], data["description"], data["price"], data.get("photo_id"))
        await state.finish()
        await message.answer(f"✅ Товар додано! (ID: {pid})", reply_markup=admin_kb())

    @dp.message_handler(Text(equals="📋 Переглянути товари"))
    async def admin_view_products(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return
        products = await get_products(limit=50, offset=0)
        if not products:
            await message.answer("📭 У каталозі поки немає товарів.")
            return
        lines = []
        for pid, name, desc, price, photo_id in products:
            lines.append(f"#{pid} — {name} | {price} грн")
        await message.answer("📋 Список товарів:\n" + "\n".join(lines))

    @dp.message_handler(Text(equals="❌ Видалити товар"))
    async def admin_delete_prompt(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return
        total = await count_products()
        await message.answer(
            f"Введіть ID товару для видалення. Усього товарів: {total}\nПриклад: 12"
        )

    @dp.message_handler(lambda m: m.text.isdigit())
    async def admin_delete_by_id(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return
        pid = int(message.text)
        ok = await delete_product(pid)
        if ok:
            await message.answer(f"✅ Товар #{pid} видалено.", reply_markup=admin_kb())
        else:
            await message.answer(f"❗ Товар #{pid} не знайдено.", reply_markup=admin_kb())
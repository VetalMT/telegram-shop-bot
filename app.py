from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from config import BOT_TOKEN
from db import create_pool
from handlers_user import user_router
from handlers_admin import admin_router
from handlers_shop import shop_router

import asyncio

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

dp.include_router(user_router)
dp.include_router(admin_router)
dp.include_router(shop_router)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await create_pool()

@app.post("/webhook/{token}")
async def telegram_webhook(request: Request, token: str):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)  # тут v3 вимагає передавати bot
    return {"ok": True}

@app.get("/")
async def root():
    return {"message": "Бот запущений!"}

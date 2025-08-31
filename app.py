import logging
from fastapi import FastAPI
from db import engine, Base
from models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.on_event("startup")
async def startup():
    # створюємо таблиці, якщо їх ще нема
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "✅ API працює на Render!"}


@app.get("/users")
async def get_users():
    async with AsyncSession(engine) as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        return {"users": [u.name for u in users]}

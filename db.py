import asyncpg
from config import DATABASE_URL

pool = None

async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

async def execute(query, *args):
    async with pool.acquire() as connection:
        return await connection.execute(query, *args)

async def fetch(query, *args):
    async with pool.acquire() as connection:
        return await connection.fetch(query, *args)

async def fetchrow(query, *args):
    async with pool.acquire() as connection:
        return await connection.fetchrow(query, *args)

import asyncpg
from config import DATABASE_URL


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(DATABASE_URL)

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    tg_id BIGINT UNIQUE NOT NULL,
                    name TEXT
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price NUMERIC(10, 2) NOT NULL,
                    photo TEXT,
                    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE
                );
            """)

    # ------------------- USERS -------------------
    async def add_user(self, tg_id, name):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (tg_id, name) 
                VALUES ($1, $2)
                ON CONFLICT (tg_id) DO NOTHING
            """, tg_id, name)

    async def get_user(self, tg_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM users WHERE tg_id = $1", tg_id)

    # ------------------- CATEGORIES -------------------
    async def add_category(self, name):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO categories (name) VALUES ($1)", name)

    async def get_categories(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM categories")

    # ------------------- PRODUCTS -------------------
    async def add_product(self, name, description, price, photo, category_id=None):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO products (name, description, price, photo, category_id)
                VALUES ($1, $2, $3, $4, $5)
            """, name, description, price, photo, category_id)

    async def delete_product(self, product_id):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM products WHERE id = $1", product_id)

    async def get_products(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT * FROM products")

    async def get_product(self, product_id):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT * FROM products WHERE id = $1", product_id)

    # ------------------- CART -------------------
    async def add_to_cart(self, tg_id, product_id):
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE tg_id = $1", tg_id)
            if not user:
                return
            await conn.execute("""
                INSERT INTO cart (user_id, product_id)
                VALUES ($1, $2)
            """, user["id"], product_id)

    async def get_cart(self, tg_id):
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT c.id, p.id as product_id, p.name, p.price, p.photo 
                FROM cart c
                JOIN users u ON c.user_id = u.id
                JOIN products p ON c.product_id = p.id
                WHERE u.tg_id = $1
            """, tg_id)

    async def remove_from_cart(self, cart_id):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM cart WHERE id = $1", cart_id)

    async def clear_cart(self, tg_id):
        async with self.pool.acquire() as conn:
            user = await conn.fetchrow("SELECT * FROM users WHERE tg_id = $1", tg_id)
            if user:
                await conn.execute("DELETE FROM cart WHERE user_id = $1", user["id"])

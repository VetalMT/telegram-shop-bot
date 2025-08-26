import os
import asyncpg
import asyncio

# Отримуємо URL бази даних з Environment Variables у Render
DATABASE_URL = os.getenv("DATABASE_URL")

# Глобальний пул підключень (для повторного використання)
pool = None

# Ініціалізація бази: створення таблиць
async def init_db():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)

    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price NUMERIC NOT NULL,
            photo_id TEXT
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            qty INT DEFAULT 1
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            full_name TEXT,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """)

# ==================
# Робота з товарами
# ==================
async def add_product(name, description, price, photo_id):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO products (name, description, price, photo_id) VALUES ($1, $2, $3, $4)",
            name, description, price, photo_id
        )

async def delete_product(product_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM products WHERE id=$1", product_id)

async def get_all_products():
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM products ORDER BY id")
        return rows

async def get_product(product_id):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM products WHERE id=$1", product_id)
        return row

# ==================
# Робота з корзиною
# ==================
async def add_to_cart(user_id, product_id, qty=1):
    async with pool.acquire() as conn:
        existing = await conn.fetchrow(
            "SELECT id, qty FROM cart WHERE user_id=$1 AND product_id=$2",
            user_id, product_id
        )
        if existing:
            await conn.execute(
                "UPDATE cart SET qty=qty+$1 WHERE id=$2",
                qty, existing["id"]
            )
        else:
            await conn.execute(
                "INSERT INTO cart (user_id, product_id, qty) VALUES ($1, $2, $3)",
                user_id, product_id, qty
            )

async def get_cart(user_id):
    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT c.id, c.qty, p.id as product_id, p.name, p.price
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id=$1
        """, user_id)
        return rows

async def clear_cart(user_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM cart WHERE user_id=$1", user_id)

# ==================
# Замовлення
# ==================
async def create_order(user_id, full_name, phone, address):
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO orders (user_id, full_name, phone, address)
            VALUES ($1, $2, $3, $4)
        """, user_id, full_name, phone, address)

# ==================
# Тест (тільки якщо запускати напряму)
# ==================
if __name__ == "__main__":
    async def test():
        await init_db()
        print("✅ База даних готова")

    asyncio.run(test())
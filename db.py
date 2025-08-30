import asyncpg
from config import DATABASE_URL


async def create_pool():
    return await asyncpg.create_pool(DATABASE_URL)


async def init_db(pool):
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price NUMERIC NOT NULL,
            photo TEXT
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            product_id INT REFERENCES products(id)
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT,
            phone TEXT,
            city TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT now()
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INT REFERENCES orders(id),
            product_id INT REFERENCES products(id)
        );
        """)


# ================== PRODUCTS ==================
async def add_product(pool, name, description, price, photo):
    async with pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO products (name, description, price, photo) VALUES ($1, $2, $3, $4)",
            name, description, price, photo
        )

async def get_products(pool):
    async with pool.acquire() as conn:
        return await conn.fetch("SELECT * FROM products ORDER BY id")

async def delete_product(pool, product_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM products WHERE id=$1", product_id)

# ================== CART ==================
async def add_to_cart(pool, user_id, product_id):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO carts (user_id, product_id) VALUES ($1, $2)", user_id, product_id)

async def get_cart(pool, user_id):
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT c.id, p.name, p.price
            FROM carts c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id=$1
        """, user_id)

async def remove_from_cart(pool, cart_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM carts WHERE id=$1", cart_id)

async def clear_cart(pool, user_id):
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM carts WHERE user_id=$1", user_id)

# ================== ORDERS ==================
async def create_order(pool, user_id, name, phone, city, address):
    async with pool.acquire() as conn:
        order_id = await conn.fetchval("""
            INSERT INTO orders (user_id, name, phone, city, address)
            VALUES ($1, $2, $3, $4, $5) RETURNING id
        """, user_id, name, phone, city, address)
        return order_id

async def add_order_item(pool, order_id, product_id):
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO order_items (order_id, product_id) VALUES ($1, $2)", order_id, product_id)

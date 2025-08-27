import psycopg
from config import DATABASE_URL

async def init_db():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    price NUMERIC(10,2) NOT NULL,
                    photo_id TEXT
                );
            """)
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS cart (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    product_id INT REFERENCES products(id) ON DELETE CASCADE
                );
            """)
            await conn.commit()

async def add_product(name, description, price, photo_id):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO products (name, description, price, photo_id) VALUES (%s, %s, %s, %s)",
                (name, description, price, photo_id)
            )
            await conn.commit()

async def delete_product(product_id):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
            await conn.commit()

async def get_products():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, description, price, photo_id FROM products")
            return await cur.fetchall()

async def add_to_cart(user_id, product_id):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO cart (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
            await conn.commit()

async def get_cart(user_id):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT p.name, p.price FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id=%s
            """, (user_id,))
            return await cur.fetchall()

async def clear_cart(user_id):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
            await conn.commit()
import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")

async def get_conn():
    return await psycopg.AsyncConnection.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)

# Отримати всі продукти
async def get_products():
    async with await get_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id, name, description, price, photo_id FROM products")
            return await cur.fetchall()

# Додати продукт у кошик
async def add_to_cart(user_id, product_id, qty=1):
    async with await get_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO carts(user_id) VALUES(%s) ON CONFLICT(user_id) DO NOTHING", (user_id,))
            await cur.execute("""
                INSERT INTO cart_items(cart_id, product_id, qty)
                SELECT id, %s, %s FROM carts WHERE user_id=%s
                ON CONFLICT(cart_id, product_id) DO UPDATE SET qty = cart_items.qty + EXCLUDED.qty
            """, (product_id, qty, user_id))

# Отримати кошик користувача
async def get_cart(user_id):
    async with await get_conn() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT ci.id, p.name, p.price, ci.qty
                FROM cart_items ci
                JOIN carts c ON ci.cart_id = c.id
                JOIN products p ON ci.product_id = p.id
                WHERE c.user_id=%s
            """, (user_id,))
            return await cur.fetchall()

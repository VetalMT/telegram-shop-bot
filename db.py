import os
import psycopg
from psycopg.rows import dict_row
from typing import List, Optional, Tuple, Dict, Any

# URL до бази з env (Render автоматично створює DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ Не вказано DATABASE_URL в змінних оточення!")

# ---------- INIT ----------
async def init_db():
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            # Products
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price REAL NOT NULL,
                photo_id TEXT
            )
            """)
            # Carts
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS carts(
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE
            )
            """)
            # Cart items
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items(
                id SERIAL PRIMARY KEY,
                cart_id INT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                qty INT NOT NULL DEFAULT 1,
                UNIQUE(cart_id, product_id)
            )
            """)
            # Orders
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS orders(
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                total REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Order items
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items(
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                qty INT NOT NULL,
                price REAL NOT NULL
            )
            """)
        await conn.commit()

# ---------- PRODUCTS ----------
async def add_product(name: str, description: str, price: float, photo_id: Optional[str]) -> int:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO products(name, description, price, photo_id) VALUES(%s,%s,%s,%s) RETURNING id",
                (name, description, price, photo_id)
            )
            (pid,) = await cur.fetchone()
            await conn.commit()
            return pid

async def get_products(limit: int = 50, offset: int = 0) -> List[Tuple]:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, name, description, price, photo_id FROM products ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            return await cur.fetchall()

async def count_products() -> int:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM products")
            (count,) = await cur.fetchone()
            return int(count)

async def get_product(product_id: int) -> Optional[Tuple]:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, name, description, price, photo_id FROM products WHERE id=%s",
                (product_id,)
            )
            return await cur.fetchone()

async def delete_product(product_id: int) -> bool:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
            await conn.commit()
            return cur.rowcount > 0

# ---------- CART ----------
async def _get_or_create_cart_id(conn, user_id: int) -> int:
    async with conn.cursor() as cur:
        await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
        row = await cur.fetchone()
        if row:
            return row[0]
        await cur.execute("INSERT INTO carts(user_id) VALUES(%s) RETURNING id", (user_id,))
        (cart_id,) = await cur.fetchone()
        return cart_id

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        cart_id = await _get_or_create_cart_id(conn, user_id)
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE cart_items SET qty=qty+%s WHERE cart_id=%s AND product_id=%s",
                (qty, cart_id, product_id)
            )
            if cur.rowcount == 0:
                await cur.execute(
                    "INSERT INTO cart_items(cart_id, product_id, qty) VALUES(%s,%s,%s)",
                    (cart_id, product_id, qty)
                )
        await conn.commit()

async def remove_from_cart(user_id: int, product_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = await cur.fetchone()
            if not cart:
                return
            cart_id = cart[0]
            await cur.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s", (cart_id, product_id))
        await conn.commit()

async def clear_cart(user_id: int):
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = await cur.fetchone()
            if not cart:
                return
            cart_id = cart[0]
            await cur.execute("DELETE FROM cart_items WHERE cart_id=%s", (cart_id,))
        await conn.commit()

async def get_cart(user_id: int) -> List[Dict[str, Any]]:
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = await cur.fetchone()
            if not cart:
                return []
            cart_id = cart[0]
            await cur.execute("""
                SELECT p.id, p.name, p.description, p.price, p.photo_id, ci.qty
                FROM cart_items ci 
                JOIN products p ON p.id = ci.product_id
                WHERE ci.cart_id=%s
            """, (cart_id,))
            rows = await cur.fetchall()
            return [
                {"product_id": pid, "name": name, "description": desc, "price": price, "photo_id": photo_id, "qty": qty}
                for pid, name, desc, price, photo_id, qty in rows
            ]

# ---------- ORDERS ----------
async def create_order(user_id: int, full_name: str, phone: str, address: str) -> Optional[int]:
    items = await get_cart(user_id)
    if not items:
        return None
    total = sum(i["price"] * i["qty"] for i in items)
    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "INSERT INTO orders(user_id, full_name, phone, address, total) VALUES(%s,%s,%s,%s,%s) RETURNING id",
                (user_id, full_name, phone, address, total)
            )
            (order_id,) = await cur.fetchone()
            for i in items:
                await cur.execute(
                    "INSERT INTO order_items(order_id, product_id, qty, price) VALUES(%s,%s,%s,%s)",
                    (order_id, i["product_id"], i["qty"], i["price"])
                )
        await conn.commit()
    await clear_cart(user_id)
    return order_id

from __future__ import annotations
import asyncio
from typing import List, Optional, Tuple, Dict, Any
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from config import DATABASE_URL

pool: AsyncConnectionPool | None = None

async def init_db():
    global pool
    if pool is None:
        pool = AsyncConnectionPool(
            conninfo=DATABASE_URL,
            min_size=1,
            max_size=10,
            open=True,
            kwargs={"autocommit": True}
        )

    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS products(
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                price NUMERIC(12,2) NOT NULL,
                photo_id TEXT
            )
            """)
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS carts(
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE
            )
            """)
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS cart_items(
                id SERIAL PRIMARY KEY,
                cart_id INT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                qty INT NOT NULL DEFAULT 1,
                UNIQUE(cart_id, product_id)
            )
            """)
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS orders(
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                total NUMERIC(12,2) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """)
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items(
                id SERIAL PRIMARY KEY,
                order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                qty INT NOT NULL,
                price NUMERIC(12,2) NOT NULL
            )
            """)

# ---------- Products ----------
async def add_product(name: str, description: str, price: float, photo_id: Optional[str]) -> int:
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO products(name, description, price, photo_id) VALUES(%s,%s,%s,%s) RETURNING id",
                (name, description, price, photo_id)
            )
            row = await cur.fetchone()
            return int(row["id"])

async def get_products(limit: int = 50, offset: int = 0) -> List[Tuple]:
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, name, description, price, photo_id FROM products ORDER BY id DESC LIMIT %s OFFSET %s",
                (limit, offset)
            )
            rows = await cur.fetchall()
            return [(r[0], r[1], r[2], float(r[3]), r[4]) for r in rows]

async def get_product(product_id: int) -> Optional[Tuple]:
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT id, name, description, price, photo_id FROM products WHERE id=%s",
                (product_id,)
            )
            row = await cur.fetchone()
            if row:
                return (row[0], row[1], row[2], float(row[3]), row[4])
            return None

async def delete_product(product_id: int) -> bool:
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
            return cur.rowcount > 0

async def count_products() -> int:
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT COUNT(*) FROM products")
            (count,) = await cur.fetchone()
            return int(count)

# ---------- Cart ----------
async def _get_or_create_cart_id(conn: psycopg.AsyncConnection, user_id: int) -> int:
    async with conn.cursor() as cur:
        await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
        row = await cur.fetchone()
        if row:
            return int(row[0])
        await cur.execute("INSERT INTO carts(user_id) VALUES(%s) RETURNING id", (user_id,))
        (cid,) = await cur.fetchone()
        return int(cid)

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    assert pool is not None
    async with pool.connection() as conn:
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

async def remove_from_cart(user_id: int, product_id: int):
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = await cur.fetchone()
            if not cart:
                return
            cart_id = int(cart[0])
            await cur.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s", (cart_id, product_id))

async def clear_cart(user_id: int):
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = await cur.fetchone()
            if not cart:
                return
            cart_id = int(cart[0])
            await cur.execute("DELETE FROM cart_items WHERE cart_id=%s", (cart_id,))

async def get_cart(user_id: int) -> List[Dict[str, Any]]:
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
            cart = await cur.fetchone()
            if not cart:
                return []
            cart_id = int(cart["id"])
            await cur.execute("""
                SELECT p.id, p.name, p.price, p.photo_id, ci.qty
                FROM cart_items ci
                JOIN products p ON p.id = ci.product_id
                WHERE ci.cart_id=%s
            """, (cart_id,))
            rows = await cur.fetchall()
            return [
                {"product_id": r["id"], "name": r["name"], "price": float(r["price"]),
                 "photo_id": r["photo_id"], "qty": r["qty"]}
                for r in rows
            ]

# ---------- Orders ----------
async def create_order(user_id: int, full_name: str, phone: str, address: str) -> Optional[int]:
    items = await get_cart(user_id)
    if not items:
        return None
    total = sum(i["price"] * i["qty"] for i in items)
    assert pool is not None
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "INSERT INTO orders(user_id, full_name, phone, address, total) "
                "VALUES(%s,%s,%s,%s,%s) RETURNING id",
                (user_id, full_name, phone, address, total)
            )
            row = await cur.fetchone()
            order_id = int(row["id"])
            for i in items:
                await cur.execute(
                    "INSERT INTO order_items(order_id, product_id, qty, price) VALUES(%s,%s,%s,%s)",
                    (order_id, i["product_id"], i["qty"], i["price"])
                )
    await clear_cart(user_id)
    return order_id
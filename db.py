import asyncpg
from typing import List, Optional, Dict, Any, Tuple
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

pool: asyncpg.Pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    async with pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            photo_id TEXT
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS carts(
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS cart_items(
            id SERIAL PRIMARY KEY,
            cart_id INTEGER NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            qty INTEGER NOT NULL DEFAULT 1,
            UNIQUE(cart_id, product_id)
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS order_items(
            id SERIAL PRIMARY KEY,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            qty INTEGER NOT NULL,
            price REAL NOT NULL
        );
        """)

# ---------- PRODUCTS ----------
async def add_product(name: str, description: str, price: float, photo_id: Optional[str]) -> int:
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "INSERT INTO products(name, description, price, photo_id) VALUES($1,$2,$3,$4) RETURNING id",
            name, description, price, photo_id
        )
        return result["id"]

async def get_products(limit: int = 50, offset: int = 0) -> List[Tuple]:
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, name, description, price, photo_id FROM products ORDER BY id DESC LIMIT $1 OFFSET $2",
            limit, offset
        )
        return [(r["id"], r["name"], r["description"], r["price"], r["photo_id"]) for r in rows]

async def count_products() -> int:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT COUNT(*) as count FROM products")
        return row["count"]

async def get_product(product_id: int) -> Optional[Tuple]:
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, description, price, photo_id FROM products WHERE id=$1",
            product_id
        )
        if row:
            return (row["id"], row["name"], row["description"], row["price"], row["photo_id"])
        return None

async def delete_product(product_id: int) -> bool:
    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM products WHERE id=$1", product_id)
        return result.endswith("1")

# ---------- CART ----------
async def _get_or_create_cart_id(conn, user_id: int) -> int:
    row = await conn.fetchrow("SELECT id FROM carts WHERE user_id=$1", user_id)
    if row:
        return row["id"]
    result = await conn.fetchrow("INSERT INTO carts(user_id) VALUES($1) RETURNING id", user_id)
    return result["id"]

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    async with pool.acquire() as conn:
        cart_id = await _get_or_create_cart_id(conn, user_id)
        result = await conn.execute(
            "UPDATE cart_items SET qty=qty+$1 WHERE cart_id=$2 AND product_id=$3",
            qty, cart_id, product_id
        )
        if result == "UPDATE 0":
            await conn.execute(
                "INSERT INTO cart_items(cart_id, product_id, qty) VALUES($1,$2,$3)",
                cart_id, product_id, qty
            )

async def remove_from_cart(user_id: int, product_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM carts WHERE user_id=$1", user_id)
        if not row:
            return
        cart_id = row["id"]
        await conn.execute("DELETE FROM cart_items WHERE cart_id=$1 AND product_id=$2", cart_id, product_id)

async def clear_cart(user_id: int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM carts WHERE user_id=$1", user_id)
        if not row:
            return
        cart_id = row["id"]
        await conn.execute("DELETE FROM cart_items WHERE cart_id=$1", cart_id)

async def get_cart(user_id: int) -> List[Dict[str, Any]]:
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT id FROM carts WHERE user_id=$1", user_id)
        if not row:
            return []
        cart_id = row["id"]
        rows = await conn.fetch("""
            SELECT p.id, p.name, p.price, p.photo_id, ci.qty
            FROM cart_items ci
            JOIN products p ON p.id = ci.product_id
            WHERE ci.cart_id=$1
        """, cart_id)
        items = []
        for r in rows:
            items.append({"product_id": r["id"], "name": r["name"], "price": r["price"], "photo_id": r["photo_id"], "qty": r["qty"]})
        return items

# ---------- ORDERS ----------
async def create_order(user_id: int, full_name: str, phone: str, address: str) -> Optional[int]:
    items = await get_cart(user_id)
    if not items:
        return None
    total = sum(i["price"] * i["qty"] for i in items)
    async with pool.acquire() as conn:
        order = await conn.fetchrow(
            "INSERT INTO orders(user_id, full_name, phone, address, total) VALUES($1,$2,$3,$4,$5) RETURNING id",
            user_id, full_name, phone, address, total
        )
        order_id = order["id"]
        for i in items:
            await conn.execute(
                "INSERT INTO order_items(order_id, product_id, qty, price) VALUES($1,$2,$3,$4)",
                order_id, i["product_id"], i["qty"], i["price"]
            )
    await clear_cart(user_id)
    return order_id

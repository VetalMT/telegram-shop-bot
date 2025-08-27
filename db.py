# db.py
import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
from typing import List, Optional, Tuple, Dict, Any
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

def _get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

# ---------- Sync DB functions (used inside run_in_executor) ----------
def _init_db_sync():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price NUMERIC(12,2) NOT NULL,
            photo_id TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS carts(
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL UNIQUE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart_items(
            id SERIAL PRIMARY KEY,
            cart_id INT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
            product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            qty INT NOT NULL DEFAULT 1,
            UNIQUE(cart_id, product_id)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            total NUMERIC(12,2) NOT NULL,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS order_items(
            id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
            qty INT NOT NULL,
            price NUMERIC(12,2) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def _add_product_sync(name: str, description: str, price: float, photo_id: Optional[str]) -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products(name, description, price, photo_id) VALUES (%s, %s, %s, %s) RETURNING id",
        (name, description, price, photo_id)
    )
    pid = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return int(pid)

def _get_products_sync(limit: int = 50, offset: int = 0) -> List[Tuple]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, description, price, photo_id FROM products ORDER BY id DESC LIMIT %s OFFSET %s",
        (limit, offset)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def _count_products_sync() -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM products")
    c = cur.fetchone()[0]
    cur.close()
    conn.close()
    return int(c)

def _get_product_sync(product_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, price, photo_id FROM products WHERE id=%s", (product_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

def _delete_product_sync(product_id: int) -> bool:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (product_id,))
    affected = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return affected > 0

def _get_or_create_cart_id_sync(user_id: int) -> int:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
    r = cur.fetchone()
    if r:
        cid = r[0]
    else:
        cur.execute("INSERT INTO carts(user_id) VALUES(%s) RETURNING id", (user_id,))
        cid = cur.fetchone()[0]
        conn.commit()
    cur.close()
    conn.close()
    return int(cid)

def _add_to_cart_sync(user_id: int, product_id: int, qty: int = 1):
    conn = _get_conn()
    cur = conn.cursor()
    cart_id = _get_or_create_cart_id_sync(user_id)
    cur.execute("UPDATE cart_items SET qty = qty + %s WHERE cart_id=%s AND product_id=%s", (qty, cart_id, product_id))
    if cur.rowcount == 0:
        cur.execute("INSERT INTO cart_items(cart_id, product_id, qty) VALUES(%s,%s,%s)", (cart_id, product_id, qty))
    conn.commit()
    cur.close()
    conn.close()

def _remove_from_cart_sync(user_id: int, product_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
    r = cur.fetchone()
    if not r:
        cur.close()
        conn.close()
        return
    cart_id = r[0]
    cur.execute("DELETE FROM cart_items WHERE cart_id=%s AND product_id=%s", (cart_id, product_id))
    conn.commit()
    cur.close()
    conn.close()

def _clear_cart_sync(user_id: int):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
    r = cur.fetchone()
    if not r:
        cur.close()
        conn.close()
        return
    cart_id = r[0]
    cur.execute("DELETE FROM cart_items WHERE cart_id=%s", (cart_id,))
    conn.commit()
    cur.close()
    conn.close()

def _get_cart_sync(user_id: int) -> List[Dict[str, Any]]:
    conn = _get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id FROM carts WHERE user_id=%s", (user_id,))
    r = cur.fetchone()
    if not r:
        cur.close()
        conn.close()
        return []
    cart_id = r['id']
    cur.execute("""
        SELECT p.id, p.name, p.price, p.photo_id, ci.qty
        FROM cart_items ci
        JOIN products p ON p.id = ci.product_id
        WHERE ci.cart_id=%s
    """, (cart_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def _create_order_sync(user_id: int, full_name: str, phone: str, address: str) -> Optional[int]:
    items = _get_cart_sync(user_id)
    if not items:
        return None
    total = sum(float(i['price']) * i['qty'] for i in items)
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders(user_id, full_name, phone, address, total) VALUES(%s,%s,%s,%s,%s) RETURNING id",
        (user_id, full_name, phone, address, total)
    )
    oid = cur.fetchone()[0]
    for i in items:
        cur.execute(
            "INSERT INTO order_items(order_id, product_id, qty, price) VALUES(%s,%s,%s,%s)",
            (oid, i['id'], i['qty'], i['price'])
        )
    conn.commit()
    cur.close()
    conn.close()
    # clear cart
    _clear_cart_sync(user_id)
    return int(oid)

# ---------- Async wrappers ----------
async def init_db():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _init_db_sync)

async def add_product(name: str, description: str, price: float, photo_id: Optional[str]) -> int:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _add_product_sync, name, description, price, photo_id)

async def get_products(limit: int = 50, offset: int = 0):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_products_sync, limit, offset)

async def count_products():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _count_products_sync)

async def get_product(product_id: int):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_product_sync, product_id)

async def delete_product(product_id: int) -> bool:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _delete_product_sync, product_id)

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _add_to_cart_sync, user_id, product_id, qty)

async def remove_from_cart(user_id: int, product_id: int):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _remove_from_cart_sync, user_id, product_id)

async def clear_cart(user_id: int):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _clear_cart_sync, user_id)

async def get_cart(user_id: int):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_cart_sync, user_id)

async def create_order(user_id: int, full_name: str, phone: str, address: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _create_order_sync, user_id, full_name, phone, address)
import aiosqlite
from typing import List, Optional, Tuple, Dict, Any

DB_PATH = "shop.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        PRAGMA foreign_keys = ON;
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            photo_id TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS carts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            UNIQUE(user_id)
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS cart_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cart_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY(cart_id) REFERENCES carts(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE,
            UNIQUE(cart_id, product_id)
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS orders(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS order_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        )
        """)
        await db.commit()

# ---------- PRODUCTS ----------
async def add_product(name: str, description: str, price: float, photo_id: Optional[str]) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO products(name, description, price, photo_id) VALUES(?,?,?,?)",
            (name, description, price, photo_id)
        )
        await db.commit()
        return cur.lastrowid

async def get_products(limit: int = 50, offset: int = 0) -> List[Tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, name, description, price, photo_id FROM products ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return await cur.fetchall()

async def count_products() -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM products")
        (count,) = await cur.fetchone()
        return int(count)

async def get_product(product_id: int) -> Optional[Tuple]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT id, name, description, price, photo_id FROM products WHERE id=?",
            (product_id,)
        )
        return await cur.fetchone()

async def delete_product(product_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM products WHERE id=?", (product_id,))
        await db.commit()
        return cur.rowcount > 0

# ---------- CART ----------
async def _get_or_create_cart_id(db, user_id: int) -> int:
    cur = await db.execute("SELECT id FROM carts WHERE user_id=?", (user_id,))
    row = await cur.fetchone()
    if row:
        return row[0]
    cur = await db.execute("INSERT INTO carts(user_id) VALUES(?)", (user_id,))
    return cur.lastrowid

async def add_to_cart(user_id: int, product_id: int, qty: int = 1):
    async with aiosqlite.connect(DB_PATH) as db:
        cart_id = await _get_or_create_cart_id(db, user_id)
        cur = await db.execute(
            "UPDATE cart_items SET qty=qty+? WHERE cart_id=? AND product_id=?",
            (qty, cart_id, product_id)
        )
        if cur.rowcount == 0:
            await db.execute(
                "INSERT INTO cart_items(cart_id, product_id, qty) VALUES(?,?,?)",
                (cart_id, product_id, qty)
            )
        await db.commit()

async def remove_from_cart(user_id: int, product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id FROM carts WHERE user_id=?", (user_id,))
        cart = await cur.fetchone()
        if not cart:
            return
        cart_id = cart[0]
        await db.execute("DELETE FROM cart_items WHERE cart_id=? AND product_id=?", (cart_id, product_id))
        await db.commit()

async def clear_cart(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id FROM carts WHERE user_id=?", (user_id,))
        cart = await cur.fetchone()
        if not cart:
            return
        cart_id = cart[0]
        await db.execute("DELETE FROM cart_items WHERE cart_id=?", (cart_id,))
        await db.commit()

async def get_cart(user_id: int) -> List[Dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id FROM carts WHERE user_id=?", (user_id,))
        cart = await cur.fetchone()
        if not cart:
            return []
        cart_id = cart[0]
        cur = await db.execute("""
            SELECT p.id, p.name, p.price, p.photo_id, ci.qty
            FROM cart_items ci 
            JOIN products p ON p.id = ci.product_id
            WHERE ci.cart_id=?
        """, (cart_id,))
        rows = await cur.fetchall()
        items = []
        for pid, name, price, photo_id, qty in rows:
            items.append({"product_id": pid, "name": name, "price": price, "photo_id": photo_id, "qty": qty})
        return items

# ---------- ORDERS ----------
async def create_order(user_id: int, full_name: str, phone: str, address: str) -> Optional[int]:
    items = await get_cart(user_id)
    if not items:
        return None
    total = sum(i["price"] * i["qty"] for i in items)
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO orders(user_id, full_name, phone, address, total) VALUES(?,?,?,?,?)",
            (user_id, full_name, phone, address, total)
        )
        order_id = cur.lastrowid
        for i in items:
            await db.execute(
                "INSERT INTO order_items(order_id, product_id, qty, price) VALUES(?,?,?,?)",
                (order_id, i["product_id"], i["qty"], i["price"])
            )
        await db.commit()
    await clear_cart(user_id)
    return order_id

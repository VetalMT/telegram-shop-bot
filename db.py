import aiosqlite

DB_PATH = "shop.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
        """)
        await db.commit()

async def add_product(name: str, description: str, price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
            (name, description, price)
        )
        await db.commit()

async def get_products():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, name, description, price FROM products")
        rows = await cursor.fetchall()
        await cursor.close()
        return [{"id": r[0], "name": r[1], "description": r[2], "price": r[3]} for r in rows]

async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id, name, description, price FROM products WHERE id = ?", (product_id,))
        row = await cursor.fetchone()
        await cursor.close()
        if row:
            return {"id": row[0], "name": row[1], "description": row[2], "price": row[3]}
        return None

async def delete_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()

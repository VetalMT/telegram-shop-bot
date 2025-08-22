import sqlite3

DB_NAME = "shop.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Таблиця товарів
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            photo TEXT
        )
    """)

    # Таблиця корзини (тимчасово, потім зробимо orders)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (user_id, product_id)
        )
    """)

    conn.commit()
    conn.close()


# --- ФУНКЦІЇ ДЛЯ РОБОТИ З ТОВАРАМИ ---

def add_product(name: str, description: str, price: float, photo: str = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name, description, price, photo) VALUES (?, ?, ?, ?)",
        (name, description, price, photo)
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()


def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, price, photo FROM products")
    products = cur.fetchall()
    conn.close()
    return products


def get_product(product_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT id, name, description, price, photo FROM products WHERE id = ?", (product_id,))
    product = cur.fetchone()
    conn.close()
    return product

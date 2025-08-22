import sqlite3

# Підключення до бази
conn = sqlite3.connect("shop.db")
cursor = conn.cursor()

# Створюємо таблицю продуктів, якщо її ще немає
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT
)
""")
conn.commit()

# Додаємо продукт
def add_product(name: str, price: float, description: str):
    cursor.execute("INSERT INTO products (name, price, description) VALUES (?, ?, ?)", (name, price, description))
    conn.commit()

# Отримати всі продукти
def get_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

# Отримати один продукт
def get_product(product_id: int):
    cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
    return cursor.fetchone()

# Видалити продукт
def delete_product(product_id: int):
    cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()

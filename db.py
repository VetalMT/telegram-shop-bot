import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.getenv("DATABASE_URL")


def init_db():
    """Створення таблиць якщо вони відсутні"""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            description TEXT,
            image_url TEXT
        )
        """)
        conn.commit()


def add_product(name: str, price: float, description: str, image_url: str):
    """Додати товар"""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(
            "INSERT INTO products (name, price, description, image_url) VALUES (%s, %s, %s, %s)",
            (name, price, description, image_url)
        )
        conn.commit()


def get_products():
    """Отримати список всіх товарів"""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        rows = conn.execute("SELECT * FROM products ORDER BY id").fetchall()
        return rows


def get_product(product_id: int):
    """Отримати один товар по ID"""
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        row = conn.execute(
            "SELECT * FROM products WHERE id = %s",
            (product_id,)
        ).fetchone()
        return row
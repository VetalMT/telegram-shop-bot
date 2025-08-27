import os
import psycopg
import asyncio

DATABASE_URL = os.getenv("DATABASE_URL")


def init_db():
    """Створюємо таблиці, якщо їх немає"""
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price NUMERIC(10,2) NOT NULL,
                    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE
                );
            """)
            conn.commit()


# =============================
#   Робота з категоріями
# =============================

async def fetch_categories():
    return await asyncio.to_thread(_fetch_categories)


def _fetch_categories():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM categories;")
            return cur.fetchall()


async def add_category(name):
    return await asyncio.to_thread(_add_category, name)


def _add_category(name):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO categories (name) VALUES (%s) ON CONFLICT DO NOTHING;", (name,))
            conn.commit()


# =============================
#   Робота з товарами
# =============================

async def fetch_products(category_id):
    return await asyncio.to_thread(_fetch_products, category_id)


def _fetch_products(category_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, price FROM products WHERE category_id = %s;", (category_id,))
            return cur.fetchall()


async def add_product(name, price, category_id):
    return await asyncio.to_thread(_add_product, name, price, category_id)


def _add_product(name, price, category_id):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products (name, price, category_id) VALUES (%s, %s, %s);",
                (name, price, category_id)
            )
            conn.commit()
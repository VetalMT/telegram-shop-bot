import os
import psycopg
from psycopg.rows import dict_row

DB_URL = os.getenv("DATABASE_URL")


def init_db():
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    price NUMERIC NOT NULL
                )
            """)
        conn.commit()


def add_item(name: str, price: float):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO items (name, price) VALUES (%s, %s)", (name, price))
        conn.commit()


def delete_item(item_id: int):
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
        conn.commit()


def get_items():
    with psycopg.connect(DB_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM items ORDER BY id")
            return cur.fetchall()
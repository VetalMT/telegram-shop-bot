-- --------------------------
-- Telegram Shop Bot DB Dump
-- --------------------------

-- ТАБЛИЦЯ ПРОДУКТІВ
CREATE TABLE IF NOT EXISTS products(
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    photo_id TEXT
);

-- КОРЗИНА КОРИСТУВАЧА
CREATE TABLE IF NOT EXISTS carts(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE
);

-- ЕЛЕМЕНТИ КОРЗИНИ
CREATE TABLE IF NOT EXISTS cart_items(
    id SERIAL PRIMARY KEY,
    cart_id INT NOT NULL REFERENCES carts(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    qty INT NOT NULL DEFAULT 1,
    UNIQUE(cart_id, product_id)
);

-- ЗАМОВЛЕННЯ
CREATE TABLE IF NOT EXISTS orders(
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    full_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    total REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ЕЛЕМЕНТИ ЗАМОВЛЕННЯ
CREATE TABLE IF NOT EXISTS order_items(
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    qty INT NOT NULL,
    price REAL NOT NULL
);

-- Приклад вставки продуктів
INSERT INTO products(name, description, price, photo_id) VALUES
('Товар 1', 'Опис товару 1', 100.0, 'photo_id_1'),
('Товар 2', 'Опис товару 2', 250.0, 'photo_id_2'),
('Товар 3', 'Опис товару 3', 50.0, NULL);

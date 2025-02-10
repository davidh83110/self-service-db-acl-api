-- DDL
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'completed', 'cancelled'))
);


-- Mock Data
INSERT INTO users (name, email) VALUES
('David Hsu', 'david.hsu@abc.com'),
('Bob James', 'bob@xyz.com'),
('Annie', 'annie@test.com');

INSERT INTO products (name, price) VALUES
('Logitech MX Keybord', 120.99),
('Apple AirPods Pro', 199),
('Apple Iphone 16', 899);

INSERT INTO orders (user_id, total_price, status) VALUES
(1, 1200.99, 'pending'),
(2, 319.99, 'completed'),
(3, 899, 'cancelled');

-- 4.1 SQL Basics: Manual Inventory Schema and Seed Data
-- Demonstrates: CREATE TABLE, PRIMARY KEY, FOREIGN KEY, UNIQUE, NOT NULL, CHECK, INSERT, UPDATE, DELETE

PRAGMA foreign_keys = ON;

-- Drop tables if they already exist to allow clean reruns
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS categories;

-- Categories lookup table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

-- Products inventory table
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    price REAL NOT NULL CHECK (price >= 0),
    status TEXT NOT NULL DEFAULT 'in_stock' CHECK (status IN ('in_stock', 'low_stock', 'out_of_stock')),
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

-- Seed Categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Electronic gadgets, computing hardware, and accessories'),
('Office Supplies', 'Desk accessories, stationery, and organizational tools'),
('Furniture', 'Office chairs, standing desks, and storage units');

-- Seed Products
INSERT INTO products (sku, name, category_id, quantity, price, status) VALUES
('ELEC-1001', 'Wireless Ergonomic Mouse', 1, 45, 49.99, 'in_stock'),
('ELEC-1002', 'Mechanical Keyboard (TKL)', 1, 18, 119.50, 'in_stock'),
('ELEC-1003', '4K USB-C Monitor 27"', 1, 4, 389.00, 'low_stock'),
('OFFC-2001', 'Heavy Duty Stapler', 2, 25, 14.75, 'in_stock'),
('OFFC-2002', 'Gel Ink Pens (12-pack)', 2, 80, 11.20, 'in_stock'),
('OFFC-2003', 'Notebook A5 Hardcover', 2, 0, 8.50, 'out_of_stock'),
('FURN-3001', 'Ergonomic Mesh Chair', 3, 12, 280.00, 'in_stock'),
('FURN-3002', 'Electric Standing Desk', 3, 3, 499.00, 'low_stock');

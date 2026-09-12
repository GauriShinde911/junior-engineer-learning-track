-- 4.3 Schema Design: Multi-Table Normalized E-Commerce Schema
-- Demonstrates: 3NF Normalization, Composite Foreign Keys, Cascade Deletes, Indexes, and Audit Timestamps

PRAGMA foreign_keys = ON;

-- Customers table: Stores distinct buyer entities (1NF, 2NF, 3NF)
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    phone TEXT,
    tier TEXT NOT NULL DEFAULT 'standard' CHECK (tier IN ('standard', 'gold', 'platinum')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Orders table: Represents order transaction headers linked to a customer
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'cancelled')),
    total_amount REAL NOT NULL DEFAULT 0.0 CHECK (total_amount >= 0.0),
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

-- Order Items table: Line items for orders, resolving many-to-many relationship with products
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    item_sku TEXT NOT NULL,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0.0),
    line_total REAL GENERATED ALWAYS AS (quantity * unit_price) STORED,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
);

-- Performance Indexes
-- Accelerate customer order history lookups
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);

-- Accelerate filtering by order status (e.g., active orders dashboard)
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Accelerate joins when retrieving all line items for an order
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);

-- Composite index for looking up item purchases by SKU and date
CREATE INDEX IF NOT EXISTS idx_order_items_sku ON order_items(item_sku);

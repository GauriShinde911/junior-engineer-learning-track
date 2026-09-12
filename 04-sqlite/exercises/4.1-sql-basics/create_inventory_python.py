"""
4.1 SQL Basics: create_inventory_python.py
Builds the inventory database schema and inserts seed data using Python's sqlite3 module.
"""

from pathlib import Path
import sqlite3
import sys

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "inventory.db"


def initialize_database(db_target: str | Path | sqlite3.Connection = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Initializes the inventory schema and populates sample records.
    Accepts a file path, ':memory:', or an existing sqlite3.Connection.
    """
    if isinstance(db_target, sqlite3.Connection):
        conn = db_target
        should_close = False
    else:
        conn = sqlite3.connect(str(db_target))
        should_close = False

    try:
        # Enforce foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON;")

        # Enable dictionary-like access to rows
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # DDL: Create Tables
        cursor.executescript("""
            DROP TABLE IF EXISTS products;
            DROP TABLE IF EXISTS categories;

            CREATE TABLE categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );

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
        """)

        # DML: Insert Categories
        categories_data = [
            ("Electronics", "Electronic gadgets, computing hardware, and accessories"),
            ("Office Supplies", "Desk accessories, stationery, and organizational tools"),
            ("Furniture", "Office chairs, standing desks, and storage units"),
        ]
        cursor.executemany(
            "INSERT INTO categories (name, description) VALUES (?, ?);",
            categories_data,
        )

        # DML: Insert Products
        products_data = [
            ("ELEC-1001", "Wireless Ergonomic Mouse", 1, 45, 49.99, "in_stock"),
            ("ELEC-1002", "Mechanical Keyboard (TKL)", 1, 18, 119.50, "in_stock"),
            ("ELEC-1003", '4K USB-C Monitor 27"', 1, 4, 389.00, "low_stock"),
            ("OFFC-2001", "Heavy Duty Stapler", 2, 25, 14.75, "in_stock"),
            ("OFFC-2002", "Gel Ink Pens (12-pack)", 2, 80, 11.20, "in_stock"),
            ("OFFC-2003", "Notebook A5 Hardcover", 2, 0, 8.50, "out_of_stock"),
            ("FURN-3001", "Ergonomic Mesh Chair", 3, 12, 280.00, "in_stock"),
            ("FURN-3002", "Electric Standing Desk", 3, 3, 499.00, "low_stock"),
        ]
        cursor.executemany(
            """INSERT INTO products (sku, name, category_id, quantity, price, status)
               VALUES (?, ?, ?, ?, ?, ?);""",
            products_data,
        )

        conn.commit()
        return conn
    finally:
        if should_close:
            conn.close()


if __name__ == "__main__":
    print(f"Initializing SQLite database at: {DEFAULT_DB_PATH}")
    connection = initialize_database(DEFAULT_DB_PATH)
    cur = connection.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM products;")
    total_products = cur.fetchone()["count"]
    print(f"Successfully initialized database with {total_products} products.")
    connection.close()

"""
4.1 SQL Basics: queries.py
Demonstrates standard SQL querying patterns in SQLite:
- Filtered SELECT with WHERE and ORDER BY
- Table JOINs (INNER JOIN)
- Aggregation with GROUP BY and HAVING
- Targeted UPDATE and DELETE statements
"""

from pathlib import Path
import sqlite3
import sys

# Ensure local module import works when run directly
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from create_inventory_python import initialize_database, DEFAULT_DB_PATH


def get_low_stock_items(conn: sqlite3.Connection, max_quantity: int = 5) -> list[dict]:
    """
    Filtered SELECT: Retrieve all products where quantity is at or below max_quantity.
    Demonstrates parameterized WHERE clause and ORDER BY.
    """
    cursor = conn.cursor()
    query = """
        SELECT id, sku, name, quantity, price, status
        FROM products
        WHERE quantity <= ?
        ORDER BY quantity ASC, price DESC;
    """
    cursor.execute(query, (max_quantity,))
    return [dict(row) for row in cursor.fetchall()]


def get_products_with_categories(conn: sqlite3.Connection) -> list[dict]:
    """
    JOIN: Join products with categories to retrieve category name alongside product details.
    Demonstrates INNER JOIN across relational tables.
    """
    cursor = conn.cursor()
    query = """
        SELECT
            p.id,
            p.sku,
            p.name AS product_name,
            c.name AS category_name,
            p.quantity,
            p.price,
            (p.quantity * p.price) AS total_value
        FROM products p
        INNER JOIN categories c ON p.category_id = c.id
        ORDER BY c.name ASC, p.name ASC;
    """
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def get_inventory_summary_by_category(conn: sqlite3.Connection) -> list[dict]:
    """
    GROUP BY: Calculate aggregate metrics (count, total units, total inventory value, average price)
    for each product category.
    Demonstrates GROUP BY, aggregate functions (COUNT, SUM, AVG, ROUND), and HAVING.
    """
    cursor = conn.cursor()
    query = """
        SELECT
            c.name AS category_name,
            COUNT(p.id) AS product_count,
            COALESCE(SUM(p.quantity), 0) AS total_units,
            ROUND(COALESCE(SUM(p.quantity * p.price), 0), 2) AS total_inventory_value,
            ROUND(COALESCE(AVG(p.price), 0), 2) AS avg_product_price
        FROM categories c
        LEFT JOIN products p ON c.id = p.category_id
        GROUP BY c.id, c.name
        HAVING product_count > 0
        ORDER BY total_inventory_value DESC;
    """
    cursor.execute(query)
    return [dict(row) for row in cursor.fetchall()]


def update_product_stock(conn: sqlite3.Connection, sku: str, new_quantity: int, new_status: str) -> bool:
    """
    UPDATE: Modify inventory quantity and status for a specific SKU.
    Returns True if a row was updated, False otherwise.
    """
    cursor = conn.cursor()
    query = """
        UPDATE products
        SET quantity = ?, status = ?
        WHERE sku = ?;
    """
    cursor.execute(query, (new_quantity, new_status, sku))
    conn.commit()
    return cursor.rowcount > 0


def delete_product(conn: sqlite3.Connection, sku: str) -> bool:
    """
    DELETE: Remove a product by SKU.
    Returns True if a row was deleted, False otherwise.
    """
    cursor = conn.cursor()
    query = "DELETE FROM products WHERE sku = ?;"
    cursor.execute(query, (sku,))
    conn.commit()
    return cursor.rowcount > 0


if __name__ == "__main__":
    conn = initialize_database(":memory:")

    print("--- 1. Low Stock Items (Threshold <= 5) ---")
    low_stock = get_low_stock_items(conn, max_quantity=5)
    for item in low_stock:
        print(f"[{item['sku']}] {item['name']} - Qty: {item['quantity']} (${item['price']})")

    print("\n--- 2. Products With Category Join ---")
    joined = get_products_with_categories(conn)
    for item in joined:
        print(f"[{item['category_name']}] {item['product_name']} | Qty: {item['quantity']} | Val: ${item['total_value']:.2f}")

    print("\n--- 3. Inventory Aggregation by Category ---")
    summary = get_inventory_summary_by_category(conn)
    for cat in summary:
        print(f"{cat['category_name']}: {cat['product_count']} items, {cat['total_units']} units, Value: ${cat['total_inventory_value']}")

    conn.close()

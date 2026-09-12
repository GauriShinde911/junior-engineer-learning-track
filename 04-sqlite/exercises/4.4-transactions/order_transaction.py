"""
4.4 Transactions: order_transaction.py
Implements an atomic multi-step order placement transaction:
1. Verify inventory stock availability for each requested item.
2. Insert master order record.
3. Insert individual order line items.
4. Decrement warehouse inventory stock.
5. Commit all changes atomically or rollback completely if any validation fails.
"""

from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass
class OrderItemRequest:
    product_id: int
    quantity: int


def setup_ecommerce_database(conn: sqlite3.Connection) -> None:
    """Sets up inventory and order tables for testing atomic transactions."""
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()
    cursor.executescript("""
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;

        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            stock_quantity INTEGER NOT NULL CHECK (stock_quantity >= 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0.0)
        );

        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            total_amount REAL NOT NULL CHECK (total_amount >= 0.0),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            unit_price REAL NOT NULL CHECK (unit_price >= 0.0),
            FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
    """)

    # Seed warehouse inventory
    cursor.executemany(
        "INSERT INTO products (name, stock_quantity, unit_price) VALUES (?, ?, ?);",
        [
            ("Wireless Mouse", 20, 25.00),
            ("Mechanical Keyboard", 5, 120.00),
            ("UltraWide Monitor 34\"", 2, 650.00),
        ],
    )
    conn.commit()


def place_order(
    conn: sqlite3.Connection,
    customer_name: str,
    items: list[OrderItemRequest],
) -> int:
    """
    Executes atomic order placement.
    Returns generated order_id upon success.
    Rolls back any partial changes if inventory is insufficient or an error occurs.
    """
    if not items:
        raise ValueError("Order must contain at least one item.")

    cursor = conn.cursor()

    try:
        # Step 1: Pre-validate all items and calculate total order price
        total_order_amount = 0.0
        validated_items = []

        for item in items:
            cursor.execute(
                "SELECT id, name, stock_quantity, unit_price FROM products WHERE id = ?;",
                (item.product_id,),
            )
            product = cursor.fetchone()

            if not product:
                raise ValueError(f"Product ID {item.product_id} does not exist.")

            prod_id, prod_name, current_stock, unit_price = product

            if item.quantity <= 0:
                raise ValueError(f"Invalid order quantity {item.quantity} for '{prod_name}'.")

            if current_stock < item.quantity:
                raise ValueError(
                    f"Insufficient inventory for '{prod_name}'. Available: {current_stock}, Requested: {item.quantity}"
                )

            item_total = item.quantity * unit_price
            total_order_amount += item_total
            validated_items.append((prod_id, item.quantity, unit_price))

        # Step 2: Insert master Order
        cursor.execute(
            "INSERT INTO orders (customer_name, total_amount) VALUES (?, ?);",
            (customer_name, total_order_amount),
        )
        order_id = cursor.lastrowid

        # Step 3: Insert Order Items and Step 4: Decrement Inventory
        for prod_id, qty, unit_price in validated_items:
            # Insert line item
            cursor.execute(
                """INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                   VALUES (?, ?, ?, ?);""",
                (order_id, prod_id, qty, unit_price),
            )
            # Decrement inventory stock
            cursor.execute(
                """UPDATE products
                   SET stock_quantity = stock_quantity - ?
                   WHERE id = ?;""",
                (qty, prod_id),
            )

        # Step 5: Atomically commit entire transaction
        conn.commit()
        return order_id

    except Exception as exc:
        conn.rollback()
        raise exc


def get_product_stock(conn: sqlite3.Connection, product_id: int) -> int:
    """Helper to check current stock level."""
    cursor = conn.cursor()
    cursor.execute("SELECT stock_quantity FROM products WHERE id = ?;", (product_id,))
    row = cursor.fetchone()
    return row[0] if row else 0


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    setup_ecommerce_database(conn)

    print("Initial Keyboard Stock:", get_product_stock(conn, 2))  # Initial is 5

    # Case 1: Valid Order
    print("\nPlacing valid order for 2 Keyboards...")
    order_id = place_order(
        conn,
        customer_name="David Miller",
        items=[OrderItemRequest(product_id=2, quantity=2)],
    )
    print(f"Order #{order_id} created successfully!")
    print("New Keyboard Stock:", get_product_stock(conn, 2))  # Should be 3

    # Case 2: Out of Stock Order (Requesting 4, only 3 left)
    print("\nPlacing invalid order (requesting 4 Keyboards, but only 3 available)...")
    try:
        place_order(
            conn,
            customer_name="Emma Watson",
            items=[OrderItemRequest(product_id=2, quantity=4)],
        )
    except ValueError as err:
        print(f"Order rejected as expected: {err}")

    print("Keyboard Stock after rollback:", get_product_stock(conn, 2))  # Must still be 3

    # Verify order was not recorded
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE customer_name = 'Emma Watson';")
    print(f"Orders for Emma in database: {cur.fetchone()[0]}")

    conn.close()

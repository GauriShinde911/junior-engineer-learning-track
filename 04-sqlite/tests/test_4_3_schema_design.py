"""
Unit tests for 4.3 Schema Design:
- schema_builder.py & schema.sql
- Multi-table relationships, cascade deletes, restrict constraints, and generated columns.
"""

from pathlib import Path
import sqlite3
import sys
import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "4.3-schema-design"
sys.path.insert(0, str(SUBSECTION_DIR))

from schema_builder import build_schema, inspect_schema


@pytest.fixture
def ecommerce_db():
    """Provides an in-memory database initialized with the e-commerce schema."""
    conn = sqlite3.connect(":memory:")
    build_schema(conn)
    yield conn
    conn.close()


def test_schema_tables_and_indexes_exist(ecommerce_db):
    """Happy Path: Verify required tables and indexes are present."""
    catalog = inspect_schema(ecommerce_db)
    assert "customers" in catalog["tables"]
    assert "orders" in catalog["tables"]
    assert "order_items" in catalog["tables"]

    # Verify key indexes exist
    index_names = " ".join(catalog["indexes"])
    assert "idx_orders_customer_id" in index_names
    assert "idx_order_items_order_id" in index_names


def test_cascade_delete_order_removes_items(ecommerce_db):
    """Happy Path: Deleting an order cascades and deletes its order_items."""
    cur = ecommerce_db.cursor()

    # Create customer
    cur.execute("INSERT INTO customers (email, full_name) VALUES ('john@example.com', 'John Doe');")
    customer_id = cur.lastrowid

    # Create order
    cur.execute(
        "INSERT INTO orders (order_number, customer_id, total_amount) VALUES ('ORD-901', ?, 150.0);",
        (customer_id,),
    )
    order_id = cur.lastrowid

    # Create order items
    cur.execute(
        """INSERT INTO order_items (order_id, item_sku, item_name, quantity, unit_price)
           VALUES (?, 'SKU-A', 'Item A', 2, 50.0);""",
        (order_id,),
    )
    cur.execute(
        """INSERT INTO order_items (order_id, item_sku, item_name, quantity, unit_price)
           VALUES (?, 'SKU-B', 'Item B', 1, 50.0);""",
        (order_id,),
    )
    ecommerce_db.commit()

    # Confirm items exist
    cur.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?;", (order_id,))
    assert cur.fetchone()[0] == 2

    # Delete order
    cur.execute("DELETE FROM orders WHERE id = ?;", (order_id,))
    ecommerce_db.commit()

    # Order items should have been cascade deleted
    cur.execute("SELECT COUNT(*) FROM order_items WHERE order_id = ?;", (order_id,))
    assert cur.fetchone()[0] == 0


def test_generated_column_calculation(ecommerce_db):
    """Happy Path: line_total generated column accurately stores quantity * unit_price."""
    cur = ecommerce_db.cursor()
    cur.execute("INSERT INTO customers (email, full_name) VALUES ('calc@test.com', 'Calc Test');")
    cust_id = cur.lastrowid
    cur.execute("INSERT INTO orders (order_number, customer_id) VALUES ('ORD-CALC', ?);", (cust_id,))
    order_id = cur.lastrowid

    cur.execute(
        """INSERT INTO order_items (order_id, item_sku, item_name, quantity, unit_price)
           VALUES (?, 'SKU-C', 'Item C', 3, 29.50);""",
        (order_id,),
    )
    ecommerce_db.commit()

    cur.execute("SELECT line_total FROM order_items WHERE order_id = ?;", (order_id,))
    assert cur.fetchone()[0] == pytest.approx(88.50)


def test_customer_deletion_restricted_by_orders(ecommerce_db):
    """Negative Case: Attempting to delete a customer who has orders is blocked by ON DELETE RESTRICT."""
    cur = ecommerce_db.cursor()
    cur.execute("INSERT INTO customers (email, full_name) VALUES ('parent@test.com', 'Parent User');")
    cust_id = cur.lastrowid

    cur.execute("INSERT INTO orders (order_number, customer_id) VALUES ('ORD-RESTRICT', ?);", (cust_id,))
    ecommerce_db.commit()

    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        cur.execute("DELETE FROM customers WHERE id = ?;", (cust_id,))


def test_invalid_order_status_rejected(ecommerce_db):
    """Negative Case: Inserting an order status outside the CHECK constraint domain fails."""
    cur = ecommerce_db.cursor()
    cur.execute("INSERT INTO customers (email, full_name) VALUES ('chk@test.com', 'Check User');")
    cust_id = cur.lastrowid

    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        cur.execute(
            "INSERT INTO orders (order_number, customer_id, status) VALUES ('ORD-BAD', ?, 'shipped_invalid');",
            (cust_id,),
        )

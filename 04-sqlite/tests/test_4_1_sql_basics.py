"""
Unit tests for 4.1 SQL Basics:
- create_inventory_python.py (schema creation & seeding)
- queries.py (filtered queries, joins, aggregates, updates, and constraint violations)
"""

from pathlib import Path
import sqlite3
import sys
import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "4.1-sql-basics"
sys.path.insert(0, str(SUBSECTION_DIR))

from create_inventory_python import initialize_database
from queries import (
    get_low_stock_items,
    get_products_with_categories,
    get_inventory_summary_by_category,
    update_product_stock,
    delete_product,
)


@pytest.fixture
def memory_db():
    """Provides a freshly seeded in-memory database."""
    conn = initialize_database(":memory:")
    yield conn
    conn.close()


def test_schema_creation_and_counts(memory_db):
    """Happy Path: Verify initial tables and seed record counts."""
    cur = memory_db.cursor()
    cur.execute("SELECT COUNT(*) FROM categories;")
    assert cur.fetchone()[0] == 3

    cur.execute("SELECT COUNT(*) FROM products;")
    assert cur.fetchone()[0] == 8


def test_low_stock_query(memory_db):
    """Happy Path: Filter low stock items with threshold."""
    items = get_low_stock_items(memory_db, max_quantity=4)
    assert len(items) > 0
    for item in items:
        assert item["quantity"] <= 4


def test_products_with_categories_join(memory_db):
    """Happy Path: Join products with category names."""
    joined = get_products_with_categories(memory_db)
    assert len(joined) == 8
    first = joined[0]
    assert "category_name" in first
    assert "total_value" in first
    assert first["total_value"] == first["quantity"] * first["price"]


def test_inventory_summary_aggregate(memory_db):
    """Happy Path: Group by aggregate calculations."""
    summary = get_inventory_summary_by_category(memory_db)
    assert len(summary) > 0
    categories = [row["category_name"] for row in summary]
    assert "Electronics" in categories
    assert "Office Supplies" in categories


def test_update_and_delete_product(memory_db):
    """Happy Path: Update product stock and delete item."""
    updated = update_product_stock(memory_db, "ELEC-1001", new_quantity=50, new_status="in_stock")
    assert updated is True

    deleted = delete_product(memory_db, "ELEC-1001")
    assert deleted is True

    # Confirm deletion
    cur = memory_db.cursor()
    cur.execute("SELECT * FROM products WHERE sku = 'ELEC-1001';")
    assert cur.fetchone() is None


def test_duplicate_sku_rejection(memory_db):
    """Negative Case: Inserting duplicate SKU violates UNIQUE constraint."""
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE constraint failed: products.sku"):
        memory_db.execute(
            """INSERT INTO products (sku, name, category_id, quantity, price)
               VALUES ('ELEC-1001', 'Duplicate Mouse', 1, 10, 20.0);"""
        )


def test_negative_quantity_check_constraint(memory_db):
    """Negative Case: Negative quantity violates CHECK constraint."""
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        memory_db.execute(
            """INSERT INTO products (sku, name, category_id, quantity, price)
               VALUES ('ELEC-9999', 'Negative Item', 1, -5, 20.0);"""
        )


def test_foreign_key_constraint(memory_db):
    """Negative Case: Assigning a non-existent category ID violates FOREIGN KEY constraint."""
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        memory_db.execute(
            """INSERT INTO products (sku, name, category_id, quantity, price)
               VALUES ('ELEC-9999', 'Ghost Category', 999, 10, 20.0);"""
        )

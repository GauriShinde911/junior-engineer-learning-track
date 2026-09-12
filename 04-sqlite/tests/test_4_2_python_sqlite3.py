"""
Unit tests for 4.2 Python sqlite3:
- db_connection.py (context managers, autocommit/rollback)
- inventory_repository.py (CRUD, parameterized queries, row mapping, duplicate rejection)
"""

from pathlib import Path
import sqlite3
import sys
import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "4.2-python-sqlite3"
sys.path.insert(0, str(SUBSECTION_DIR))

from db_connection import configure_connection, get_connection, get_cursor
from inventory_repository import InventoryItem, InventoryRepository


@pytest.fixture
def repo():
    """Returns an InventoryRepository backed by an in-memory SQLite connection."""
    conn = sqlite3.connect(":memory:")
    repository = InventoryRepository(conn)
    yield repository
    conn.close()


def test_create_and_read_item(repo):
    """Happy Path: Create an item and retrieve by ID and SKU."""
    item = InventoryItem(None, "SKU-100", "Ergonomic Keyboard", "Peripherals", 15, 89.99)
    created = repo.create(item)

    assert created.id is not None
    assert created.sku == "SKU-100"

    fetched_by_id = repo.get_by_id(created.id)
    assert fetched_by_id is not None
    assert fetched_by_id.name == "Ergonomic Keyboard"
    assert fetched_by_id.unit_price == 89.99

    fetched_by_sku = repo.get_by_sku("SKU-100")
    assert fetched_by_sku is not None
    assert fetched_by_sku.id == created.id


def test_update_item(repo):
    """Happy Path: Update quantity and price of an existing record."""
    item = repo.create(InventoryItem(None, "SKU-200", "USB Mouse", "Peripherals", 10, 19.99))
    item.quantity = 25
    item.unit_price = 17.50

    updated = repo.update(item)
    assert updated is True

    reloaded = repo.get_by_id(item.id)
    assert reloaded.quantity == 25
    assert reloaded.unit_price == 17.50


def test_delete_item(repo):
    """Happy Path: Delete an item by ID."""
    item = repo.create(InventoryItem(None, "SKU-300", "Webcam HD", "Video", 5, 49.00))
    deleted = repo.delete(item.id)
    assert deleted is True

    assert repo.get_by_id(item.id) is None


def test_parameterized_query_handles_special_characters(repo):
    """Happy Path: Names with apostrophes and SQL characters are handled safely without injection."""
    tricky_name = "O'Connor's \"Special\" Cable; DROP TABLE inventory_items;--"
    item = repo.create(InventoryItem(None, "SKU-SAFE", tricky_name, "Cables", 50, 12.00))

    retrieved = repo.get_by_sku("SKU-SAFE")
    assert retrieved is not None
    assert retrieved.name == tricky_name


def test_duplicate_sku_raises_error(repo):
    """Negative Case: Inserting an item with an existing SKU raises ValueError."""
    repo.create(InventoryItem(None, "SKU-DUP", "First Item", "Misc", 5, 10.0))
    with pytest.raises(ValueError, match="Failed to create item 'SKU-DUP'"):
        repo.create(InventoryItem(None, "SKU-DUP", "Second Item", "Misc", 10, 15.0))


def test_update_item_without_id_raises_error(repo):
    """Negative Case: Attempting to update an item where id is None raises ValueError."""
    unsaved = InventoryItem(None, "SKU-NOID", "Unsaved Item", "Misc", 1, 1.0)
    with pytest.raises(ValueError, match="Cannot update an item without a valid ID"):
        repo.update(unsaved)


def test_connection_context_manager_rollback_on_exception(tmp_path):
    """Negative Case: Unhandled exception inside get_connection triggers transaction rollback."""
    db_file = tmp_path / "test_trans.db"

    # Initialize table
    with get_connection(db_file) as conn:
        conn.execute("CREATE TABLE test_data (val TEXT);")

    # Attempt insert but raise exception inside block
    with pytest.raises(RuntimeError, match="Intentional failure"):
        with get_connection(db_file) as conn:
            conn.execute("INSERT INTO test_data (val) VALUES ('uncommitted');")
            raise RuntimeError("Intentional failure")

    # Verify that the uncommitted row was rolled back
    with get_connection(db_file) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM test_data;")
        assert cursor.fetchone()[0] == 0

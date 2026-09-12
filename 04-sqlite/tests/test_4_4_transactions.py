"""
Unit tests for 4.4 Transactions:
- transfer_exercise.py (atomic fund transfers, rollback on failure, overdraft prevention)
- order_transaction.py (atomic multi-step order placement, inventory deductions, all-or-nothing rollback)
"""

from pathlib import Path
import sqlite3
import sys
import pytest

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "4.4-transactions"
sys.path.insert(0, str(SUBSECTION_DIR))

from transfer_exercise import get_account, init_accounts_table, transfer_funds
from order_transaction import (
    OrderItemRequest,
    get_product_stock,
    place_order,
    setup_ecommerce_database,
)


# --- Transfer Exercise Tests ---

@pytest.fixture
def transfer_db():
    conn = sqlite3.connect(":memory:")
    init_accounts_table(conn)
    yield conn
    conn.close()


def test_transfer_funds_happy_path(transfer_db):
    """Happy Path: Funds transfer successfully deducts sender and credits recipient."""
    success = transfer_funds(transfer_db, from_account_id=1, to_account_id=2, amount=100.0)
    assert success is True

    alice = get_account(transfer_db, 1)
    bob = get_account(transfer_db, 2)
    assert alice.balance == 400.00
    assert bob.balance == 350.00


def test_transfer_funds_rollback_on_failure(transfer_db):
    """Negative Case: Simulated crash midway triggers complete rollback without partial balance changes."""
    alice_before = get_account(transfer_db, 1).balance
    bob_before = get_account(transfer_db, 2).balance

    with pytest.raises(RuntimeError, match="SIMULATED SYSTEM CRASH"):
        transfer_funds(
            transfer_db,
            from_account_id=1,
            to_account_id=2,
            amount=50.0,
            simulate_failure=True,
        )

    # Balances must be exactly unchanged
    alice_after = get_account(transfer_db, 1).balance
    bob_after = get_account(transfer_db, 2).balance
    assert alice_after == alice_before
    assert bob_after == bob_before


def test_transfer_insufficient_funds_rejected(transfer_db):
    """Negative Case: Attempting to transfer more than available balance is blocked."""
    with pytest.raises(ValueError, match="Insufficient funds"):
        transfer_funds(transfer_db, from_account_id=3, to_account_id=1, amount=1000.0)


# --- Order Transaction Tests ---

@pytest.fixture
def order_db():
    conn = sqlite3.connect(":memory:")
    setup_ecommerce_database(conn)
    yield conn
    conn.close()


def test_order_placement_atomic_happy_path(order_db):
    """Happy Path: Creates order, order_items, and decrements product inventory."""
    initial_mouse_stock = get_product_stock(order_db, 1)  # 20
    initial_keyboard_stock = get_product_stock(order_db, 2)  # 5

    order_id = place_order(
        order_db,
        customer_name="Samantha Ray",
        items=[
            OrderItemRequest(product_id=1, quantity=3),
            OrderItemRequest(product_id=2, quantity=2),
        ],
    )

    assert order_id is not None and order_id > 0
    assert get_product_stock(order_db, 1) == initial_mouse_stock - 3
    assert get_product_stock(order_db, 2) == initial_keyboard_stock - 2

    # Verify order total amount
    cur = order_db.cursor()
    cur.execute("SELECT total_amount FROM orders WHERE id = ?;", (order_id,))
    expected_total = (3 * 25.00) + (2 * 120.00)
    assert cur.fetchone()[0] == pytest.approx(expected_total)


def test_order_placement_rollback_on_out_of_stock(order_db):
    """Negative Case: If any item in the order exceeds available stock, entire transaction rolls back."""
    initial_mouse_stock = get_product_stock(order_db, 1)  # 20
    initial_monitor_stock = get_product_stock(order_db, 3)  # 2

    # Request 2 mice (available) and 5 monitors (only 2 available)
    with pytest.raises(ValueError, match="Insufficient inventory for 'UltraWide Monitor 34\"'"):
        place_order(
            order_db,
            customer_name="Greedy Buyer",
            items=[
                OrderItemRequest(product_id=1, quantity=2),
                OrderItemRequest(product_id=3, quantity=5),
            ],
        )

    # Mouse stock must NOT be decremented (zero side effects)
    assert get_product_stock(order_db, 1) == initial_mouse_stock
    assert get_product_stock(order_db, 3) == initial_monitor_stock

    # No order record should have been saved
    cur = order_db.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE customer_name = 'Greedy Buyer';")
    assert cur.fetchone()[0] == 0

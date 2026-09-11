"""
Tests for 1.3 Collections
Covers: inventory, employee_directory, transaction_aggregation.
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.3-collections"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from inventory import (
    calculate_total_inventory_value,
    create_price_lookup,
    get_low_stock_items,
    get_top_valued_items,
    restock_item
)
from employee_directory import (
    calculate_average_salary,
    demonstrate_mutation_vs_copy,
    find_employee_by_name,
    get_unique_departments,
    safe_add_employee
)
from transaction_aggregation import (
    filter_transactions_above,
    find_highest_spending_category,
    group_totals_by_category,
    group_totals_by_category_and_month
)


# =====================================================================
# Inventory Tests
# =====================================================================
def test_inventory_operations():
    items = [
        {"name": "Apples", "qty": 10, "price": 2.0},
        {"name": "Bananas", "qty": 4, "price": 1.5}
    ]
    assert calculate_total_inventory_value(items) == 26.0
    assert len(get_low_stock_items(items, threshold=5)) == 1
    assert create_price_lookup(items) == {"Apples": 2.0, "Bananas": 1.5}

    assert restock_item(items, "apples", 5) is True
    assert items[0]["qty"] == 15

    top = get_top_valued_items(items, n=1)
    assert top[0]["name"] == "Apples"


def test_inventory_restock_negative_quantity():
    items = [{"name": "Widget", "qty": 2, "price": 10.0}]
    with pytest.raises(ValueError, match="must be positive"):
        restock_item(items, "Widget", -5)


# =====================================================================
# Employee Directory Tests
# =====================================================================
def test_employee_directory():
    directory = [
        {"id": (1, "ENG"), "name": "Alice", "dept": "Engineering", "salary": 100000},
        {"id": (2, "HR"),  "name": "Bob",   "dept": "HR",          "salary": 60000}
    ]

    assert get_unique_departments(directory) == {"Engineering", "HR"}
    assert calculate_average_salary(directory) == 80000.0
    assert find_employee_by_name(directory, "alice")["salary"] == 100000
    assert find_employee_by_name(directory, "charlie") is None

    new_dir = safe_add_employee(directory, (3, "MKT"), "Charlie", "Marketing", 70000)
    assert len(new_dir) == 3
    assert len(directory) == 2  # Original immutable/unaffected


def test_employee_directory_empty_average():
    assert calculate_average_salary([]) == 0.0


def test_demonstrate_mutation_vs_copy():
    results = demonstrate_mutation_vs_copy()
    assert results["alias_mutates_original"] is True
    assert results["shallow_list_length_isolated"] is True
    assert results["shallow_nested_still_shared"] is True
    assert results["deep_copy_fully_isolated"] is True


# =====================================================================
# Transaction Aggregation Tests
# =====================================================================
def test_transaction_aggregation():
    txs = [
        {"category": "Food", "amount": 25.0, "month": "2026-01"},
        {"category": "Food", "amount": 15.0, "month": "2026-01"},
        {"category": "Travel", "amount": 60.0, "month": "2026-02"}
    ]
    totals = group_totals_by_category(txs)
    assert totals["Food"] == 40.0
    assert totals["Travel"] == 60.0

    monthly = group_totals_by_category_and_month(txs)
    assert monthly[("Food", "2026-01")] == 40.0

    top_cat, top_amt = find_highest_spending_category(txs)
    assert top_cat == "Travel"
    assert top_amt == 60.0

    filtered = filter_transactions_above(txs, 20.0)
    assert len(filtered) == 2


def test_transaction_aggregation_empty():
    assert find_highest_spending_category([]) == (None, 0.0)

"""
Tests for Independent Challenge: CLI Expense Tracker
Covers: models, storage (CSV/JSON import/export, error tolerance, summarization).
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
TRACKER_DIR = MODULE_ROOT / "independent" / "expense_tracker"
if str(TRACKER_DIR) not in sys.path:
    sys.path.insert(0, str(TRACKER_DIR))

from models import Expense
from storage import ExpenseStore


# =====================================================================
# Expense Model Tests
# =====================================================================
def test_expense_creation_valid():
    exp = Expense(category="groceries", amount=45.5, date_str="2026-01-05", description="Weekly run")
    assert exp.category == "Groceries"
    assert exp.amount == 45.50
    assert exp.date_str == "2026-01-05"
    assert exp.description == "Weekly run"
    assert len(exp.id) > 0


def test_expense_validation_errors():
    with pytest.raises(ValueError, match="category cannot be empty"):
        Expense(category="", amount=10.0)

    with pytest.raises(ValueError, match="strictly greater than 0"):
        Expense(category="Dining", amount=-5.0)

    with pytest.raises(ValueError, match="strictly greater than 0"):
        Expense(category="Dining", amount=0.0)

    with pytest.raises(ValueError, match="Date must follow YYYY-MM-DD"):
        Expense(category="Dining", amount=15.0, date_str="01-05-2026")


# =====================================================================
# ExpenseStore Operations Tests
# =====================================================================
def test_store_lifecycle_and_summaries():
    store = ExpenseStore()
    e1 = Expense(category="Food", amount=20.0)
    e2 = Expense(category="Food", amount=30.0)
    e3 = Expense(category="Travel", amount=50.0)

    store.add(e1)
    store.add(e2)
    store.add(e3)

    assert len(store.get_all()) == 3
    assert store.get_total_spent() == 100.0

    summary = store.get_summary_by_category()
    assert summary["Food"] == 50.0
    assert summary["Travel"] == 50.0

    assert store.delete(e1.id) is True
    assert len(store.get_all()) == 2
    assert store.delete("NON_EXISTENT_ID") is False


# =====================================================================
# File Import / Export Resilience Tests
# =====================================================================
def test_store_csv_import_resilience(tmp_path):
    csv_file = tmp_path / "mixed.csv"
    csv_file.write_text(
        "date,category,amount,description\n"
        "2026-01-01,Groceries,40.0,Milk and bread\n"
        "MALFORMED_ROW_NO_AMOUNT\n"
        "2026-01-02,Dining,-10.0,Negative should skip\n"
        "2026-01-03,Transit,5.50,Subway\n",
        encoding="utf-8"
    )

    store = ExpenseStore()
    imported, skipped = store.import_from_csv(csv_file)
    assert imported == 2
    assert skipped == 2
    assert store.get_total_spent() == 45.50


def test_store_csv_export_and_reimport(tmp_path):
    out_csv = tmp_path / "exported.csv"
    store = ExpenseStore()
    store.add(Expense(category="Coffee", amount=4.75, date_str="2026-01-10"))

    count = store.export_to_csv(out_csv)
    assert count == 1
    assert out_csv.exists()

    new_store = ExpenseStore()
    new_store.import_from_csv(out_csv)
    assert len(new_store.get_all()) == 1
    assert new_store.get_all()[0].category == "Coffee"


def test_store_json_export_and_import(tmp_path):
    json_file = tmp_path / "expenses.json"
    store = ExpenseStore()
    store.add(Expense(category="Gadgets", amount=120.0, description="Wireless ear buds"))

    store.export_to_json(json_file)
    assert json_file.exists()

    reloaded_store = ExpenseStore()
    imported = reloaded_store.import_from_json(json_file)
    assert imported == 1
    assert reloaded_store.get_all()[0].amount == 120.0


def test_store_missing_file_raises_error():
    store = ExpenseStore()
    with pytest.raises(FileNotFoundError):
        store.import_from_csv("non_existent_file_xyz.csv")

    with pytest.raises(FileNotFoundError):
        store.import_from_json("non_existent_file_xyz.json")

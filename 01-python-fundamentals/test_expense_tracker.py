import os
import pytest
from expense_tracker import (
    add_expense,
    calculate_category_summary,
    import_expenses_from_csv,
    export_expenses_to_json,
    validate_expense
)

# Test 1: Normal case - adding expenses and calculating category summaries
def test_add_expense_and_summary():
    expenses = []
    add_expense(expenses, "2026-01-01", "Food", 25.50)
    add_expense(expenses, "2026-01-02", "Food", 14.50)
    add_expense(expenses, "2026-01-02", "Transport", 10.00)
    
    assert len(expenses) == 3
    summary = calculate_category_summary(expenses)
    assert summary["Food"] == 40.00
    assert summary["Transport"] == 10.00

# Test 2: Edge case - Bad CSV rows should be skipped, valid rows imported
def test_import_csv_with_bad_rows(tmp_path):
    csv_file = tmp_path / "mixed_expenses.csv"
    csv_file.write_text(
        "date,category,amount\n"
        "2026-01-01,Groceries,50.00\n"
        "2026-01-02,INVALID_ROW_MISSING_COLS\n"
        "2026-01-03,Dining,-20.00\n"       # negative amount
        "2026-01-04,,15.00\n"              # missing category
        "2026-01-05,Utilities,80.50\n",
        encoding="utf-8"
    )
    
    imported, skipped = import_expenses_from_csv(str(csv_file))
    
    # Only the two valid rows should be imported
    assert len(imported) == 2
    assert skipped == 3
    assert imported[0]["category"] == "Groceries"
    assert imported[0]["amount"] == 50.00
    assert imported[1]["category"] == "Utilities"
    assert imported[1]["amount"] == 80.50

# Test 3: Edge case - Missing file should raise FileNotFoundError
def test_import_missing_file():
    with pytest.raises(FileNotFoundError):
        import_expenses_from_csv("non_existent_file_12345.csv")

# Test 4: Edge case - Negative amount should raise ValueError
def test_add_negative_amount():
    expenses = []
    with pytest.raises(ValueError, match="amount must be greater than zero"):
        add_expense(expenses, "2026-01-01", "Coffee", -4.50)

# Test 5: Edge case - Missing category should raise ValueError
def test_add_empty_category():
    expenses = []
    with pytest.raises(ValueError, match="category cannot be empty"):
        add_expense(expenses, "2026-01-01", "", 15.00)

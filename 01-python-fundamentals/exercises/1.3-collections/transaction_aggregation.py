"""
1.3 Collections: Transaction Aggregation
Demonstrates: Grouping with dictionaries, tuple keys for composite grouping,
filtering nested structures, and sorting key-value pairs.
"""

TRANSACTIONS = [
    {"id": "tx1", "category": "Groceries",     "amount": 45.50, "month": "2026-01"},
    {"id": "tx2", "category": "Utilities",     "amount": 120.00, "month": "2026-01"},
    {"id": "tx3", "category": "Groceries",     "amount": 32.10, "month": "2026-01"},
    {"id": "tx4", "category": "Entertainment", "amount": 15.00, "month": "2026-02"},
    {"id": "tx5", "category": "Utilities",     "amount": 65.25, "month": "2026-02"},
    {"id": "tx6", "category": "Groceries",     "amount": 88.40, "month": "2026-02"}
]


def group_totals_by_category(records: list) -> dict:
    """Sum transaction amounts grouped by category."""
    totals = {}
    for item in records:
        cat = item["category"]
        amt = item["amount"]
        totals[cat] = round(totals.get(cat, 0.0) + amt, 2)
    return totals


def group_totals_by_category_and_month(records: list) -> dict:
    """
    Demonstrates using an immutable tuple (category, month) as a composite dictionary key.
    """
    composite_totals = {}
    for item in records:
        key = (item["category"], item["month"])
        composite_totals[key] = round(composite_totals.get(key, 0.0) + item["amount"], 2)
    return composite_totals


def find_highest_spending_category(records: list) -> tuple:
    """
    Return (category, total_amount) for the highest spend category.
    Returns (None, 0.0) if records is empty.
    """
    if not records:
        return (None, 0.0)
    category_totals = group_totals_by_category(records)
    highest_cat = max(category_totals.items(), key=lambda pair: pair[1])
    return highest_cat


def filter_transactions_above(records: list, threshold: float) -> list:
    """Return all transactions with amount strictly greater than threshold."""
    return [tx for tx in records if tx["amount"] > threshold]


if __name__ == "__main__":
    print("=== Transaction Aggregator Demo ===")
    cat_totals = group_totals_by_category(TRANSACTIONS)
    print("Category Breakdown:")
    for cat, total in sorted(cat_totals.items()):
        print(f" - {cat:<15}: ${total:.2f}")

    top_cat, top_amt = find_highest_spending_category(TRANSACTIONS)
    print(f"\nTop Spending Category: {top_cat} (${top_amt:.2f})")

    monthly = group_totals_by_category_and_month(TRANSACTIONS)
    print("\nComposite (Category, Month) Totals:")
    for (cat, month), total in monthly.items():
        print(f" - {cat} ({month}): ${total:.2f}")

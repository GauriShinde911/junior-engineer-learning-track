"""
CLI interface module for Expense Tracker.
Handles user prompts, menu loops, tabular listings, and user interactions.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .models import Expense
    from .storage import ExpenseStore
except ImportError:
    from models import Expense
    from storage import ExpenseStore


def print_expense_table(expenses: list) -> None:
    if not expenses:
        print("No expenses recorded yet.\n")
        return

    print("-" * 75)
    print(f"{'ID':<10} | {'Date':<12} | {'Category':<16} | {'Amount':>10} | {'Description'}")
    print("-" * 75)
    for exp in expenses:
        print(f"{exp.id:<10} | {exp.date_str:<12} | {exp.category:<16} | ${exp.amount:>9.2f} | {exp.description}")
    print("-" * 75 + "\n")


def print_summary(store: ExpenseStore) -> None:
    all_exp = store.get_all()
    if not all_exp:
        print("No expenses recorded to summarize.\n")
        return

    total = store.get_total_spent()
    category_summary = store.get_summary_by_category()

    print("========================================")
    print("        EXPENSE SPENDING SUMMARY        ")
    print("========================================")
    print(f"Total Transactions: {len(all_exp)}")
    print(f"Total Expenditure:  ${total:,.2f}\n")
    print("Category Breakdown:")
    for cat, subtotal in sorted(category_summary.items(), key=lambda p: -p[1]):
        pct = (subtotal / total * 100) if total > 0 else 0
        print(f" - {cat:<18}: ${subtotal:>8.2f} ({pct:>5.1f}%)")
    print("========================================\n")


def run_cli(store: Optional[ExpenseStore] = None) -> None:
    if store is None:
        store = ExpenseStore()

    print("========================================")
    print("       CLI EXPENSE & ASSET TRACKER      ")
    print("========================================")

    while True:
        print("1. Add New Expense")
        print("2. List All Expenses")
        print("3. View Category Summary")
        print("4. Import from CSV")
        print("5. Export to CSV")
        print("6. Export to JSON")
        print("7. Delete an Expense")
        print("8. Exit")

        choice = input("\nSelect option (1-8): ").strip()

        if choice == "1":
            print("\n--- Add New Expense ---")
            cat = input("Category (e.g. Food, Travel, Utilities): ").strip()
            raw_amt = input("Amount ($): ").strip()
            date_input = input(f"Date [default: {datetime.now().strftime('%Y-%m-%d')}]: ").strip()
            if not date_input:
                date_input = datetime.now().strftime("%Y-%m-%d")
            desc = input("Description (optional): ").strip()

            try:
                exp = Expense(
                    category=cat,
                    amount=float(raw_amt),
                    date_str=date_input,
                    description=desc
                )
                store.add(exp)
                print(f"✓ Expense #{exp.id} recorded successfully!\n")
            except ValueError as err:
                print(f"✗ Failed to add expense: {err}\n")

        elif choice == "2":
            print("\n--- Current Expenses ---")
            print_expense_table(store.get_all())

        elif choice == "3":
            print_summary(store)

        elif choice == "4":
            path_str = input("Enter path to CSV file: ").strip()
            try:
                imported, skipped = store.import_from_csv(path_str)
                print(f"✓ Successfully imported {imported} records (Skipped {skipped} invalid rows).\n")
            except Exception as err:
                print(f"✗ Import error: {err}\n")

        elif choice == "5":
            path_str = input("Enter destination CSV file path: ").strip()
            try:
                count = store.export_to_csv(path_str)
                print(f"✓ Exported {count} records to {path_str}\n")
            except Exception as err:
                print(f"✗ Export error: {err}\n")

        elif choice == "6":
            path_str = input("Enter destination JSON file path: ").strip()
            try:
                count = store.export_to_json(path_str)
                print(f"✓ Exported {count} records to {path_str}\n")
            except Exception as err:
                print(f"✗ Export error: {err}\n")

        elif choice == "7":
            exp_id = input("Enter Expense ID to delete: ").strip()
            if store.delete(exp_id):
                print(f"✓ Expense #{exp_id} removed.\n")
            else:
                print(f"✗ No expense found with ID '{exp_id}'.\n")

        elif choice == "8":
            print("Exiting Expense Tracker. Goodbye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 8.\n")

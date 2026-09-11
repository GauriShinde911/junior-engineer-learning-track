"""
Main entry point for CLI Expense Tracker.
Can be executed directly: python main.py
"""

import sys
from pathlib import Path

# Add current directory to path if needed for local module resolution
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from cli import run_cli
from models import Expense
from storage import ExpenseStore


def main():
    store = ExpenseStore()

    # Automatically load sample data if present in data/
    sample_file = CURRENT_DIR / "data" / "sample_expenses.csv"
    if sample_file.exists():
        imported, _ = store.import_from_csv(sample_file)

    run_cli(store)


if __name__ == "__main__":
    main()

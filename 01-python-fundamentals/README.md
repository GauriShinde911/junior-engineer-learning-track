# 01 - Python Fundamentals & Expense Tracker

This folder has my day-to-day Python practice scripts covering data structures, loops, file handling, and custom error handling.

The main mini-project here is `expense_tracker.py`, which pulls together logic from my earlier calculator and aggregator practice.

---

## What `expense_tracker.py` Does

It's a simple CLI expense manager that:
- Lets you add expenses manually (`date`, `category`, `amount`).
- Imports expenses from a `.csv` file (`date,category,amount`). If a row is corrupted, has negative numbers, or is missing fields, it skips that row with a warning instead of crashing the whole script.
- Calculates and prints spending summaries grouped by category.
- Exports recorded expenses out to a clean `.json` file.

---

## Other Practice Scripts in This Folder

- `calculator.py` — basic math functions with divide-by-zero checks
- `unit_converter.py` — km/miles and C/F converter with a menu loop
- `grade_calculator.py` — score to letter grade mapping using if/elif
- `pattern_generator.py` — nested loop star triangle
- `inventory.py` — list of dictionaries and stock threshold filtering
- `employee_directory.py` — dict searches + a demo of the list copy vs alias bug
- `transaction_aggregator.py` — grouping spend totals by category
- `log_parser.py` — custom `InvalidLogFormat` exception and reading `sample.log`

---

## How to Run

### 1. Run the expense tracker
```bash
python expense_tracker.py
```

### 2. Run the tests
```bash
python -m pytest test_expense_tracker.py
```

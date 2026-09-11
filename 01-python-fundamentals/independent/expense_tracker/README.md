# CLI Expense & Asset Tracker

An independent, modular Command Line Interface (CLI) application for recording, categorizing, and analyzing personal expenses and cash outflows using only the Python standard library.

---

## Features
- **Validation**: Enforces non-empty categories, strictly positive amounts, and ISO date formatting (`YYYY-MM-DD`).
- **Resilient File I/O**: Imports CSV data while gracefully skipping corrupted or malformed rows without process termination.
- **Export Formats**: Exports expense histories to structured `.csv` and formatted `.json`.
- **Spending Analytics**: Computes total expenditures and percentage breakdowns grouped by category.
- **Modular Design**: Separated into domain entity modeling (`models.py`), storage & persistence (`storage.py`), and user interface (`cli.py`).

---

## Folder Structure
```
independent/expense_tracker/
├── main.py        <- Application entry point
├── models.py      <- Expense dataclass with strict validation
├── storage.py     <- In-memory store with CSV and JSON import/export
├── cli.py         <- Menu loop and formatted table presentation
├── data/
│   └── sample_expenses.csv <- Sample transactions with edge cases
└── README.md      <- Usage documentation
```

---

## How to Run

### Interactive Mode
Run the main script:
```bash
python independent/expense_tracker/main.py
```

### Running Automated Tests
Execute the test suite via pytest from the root folder:
```bash
python -m pytest 01-python-fundamentals/tests/test_independent_expense_tracker.py
```

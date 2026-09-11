"""
Storage module for CLI Expense Tracker.
Manages in-memory expenses, CSV/JSON file persistence, and summary calculations.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from .models import Expense
except ImportError:
    from models import Expense


class ExpenseStore:
    def __init__(self):
        self._expenses: List[Expense] = []

    def add(self, expense: Expense) -> None:
        self._expenses.append(expense)

    def delete(self, expense_id: str) -> bool:
        target = expense_id.strip().upper()
        for idx, exp in enumerate(self._expenses):
            if exp.id.upper() == target:
                del self._expenses[idx]
                return True
        return False

    def get_all(self) -> List[Expense]:
        return list(self._expenses)

    def clear(self) -> None:
        self._expenses.clear()

    def get_total_spent(self) -> float:
        return round(sum(exp.amount for exp in self._expenses), 2)

    def get_summary_by_category(self) -> Dict[str, float]:
        summary: Dict[str, float] = {}
        for exp in self._expenses:
            cat = exp.category
            summary[cat] = round(summary.get(cat, 0.0) + exp.amount, 2)
        return summary

    def import_from_csv(self, filepath: Union[str, Path]) -> Tuple[int, int]:
        """
        Imports expenses from CSV (expected columns: date, category, amount, [description]).
        Corrupt or invalid rows are skipped with a warning count returned.
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        imported_count = 0
        skipped_count = 0

        with open(path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)

            # Map column indices from header if available
            col_map = {}
            if header:
                lower_header = [h.strip().lower() for h in header]
                for idx, col_name in enumerate(lower_header):
                    col_map[col_name] = idx

            for row_no, row in enumerate(reader, start=2):
                if not row or not any(c.strip() for c in row):
                    continue

                if len(row) < 3:
                    skipped_count += 1
                    continue

                # Determine column positions based on header map or fallback
                if "category" in col_map and "amount" in col_map and "date" in col_map:
                    date_val = row[col_map["date"]].strip()
                    cat_val = row[col_map["category"]].strip()
                    amt_val = row[col_map["amount"]].strip()
                    desc_idx = col_map.get("description")
                    desc_val = row[desc_idx].strip() if desc_idx is not None and desc_idx < len(row) else ""
                    id_idx = col_map.get("id")
                    id_val = row[id_idx].strip() if id_idx is not None and id_idx < len(row) else None
                else:
                    # Fallback for headerless CSVs: if row[0] has date format (YYYY-MM-DD), assume date,cat,amt
                    # otherwise if row[1] has date format, assume id,date,cat,amt
                    if "-" in row[0] and len(row[0].strip()) == 10:
                        id_val = None
                        date_val = row[0].strip()
                        cat_val = row[1].strip()
                        amt_val = row[2].strip()
                        desc_val = row[3].strip() if len(row) > 3 else ""
                    else:
                        id_val = row[0].strip()
                        date_val = row[1].strip() if len(row) > 1 else ""
                        cat_val = row[2].strip() if len(row) > 2 else ""
                        amt_val = row[3].strip() if len(row) > 3 else ""
                        desc_val = row[4].strip() if len(row) > 4 else ""

                try:
                    kwargs = {
                        "date_str": date_val,
                        "category": cat_val,
                        "amount": float(amt_val),
                        "description": desc_val
                    }
                    if id_val:
                        kwargs["id"] = id_val
                    exp = Expense(**kwargs)
                    self.add(exp)
                    imported_count += 1
                except (ValueError, TypeError):
                    skipped_count += 1

        return imported_count, skipped_count

    def export_to_csv(self, filepath: Union[str, Path]) -> int:
        """Exports all expenses to CSV."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "category", "amount", "description"])
            for exp in self._expenses:
                writer.writerow([exp.id, exp.date_str, exp.category, f"{exp.amount:.2f}", exp.description])

        return len(self._expenses)

    def import_from_json(self, filepath: Union[str, Path]) -> int:
        """Imports expenses from a JSON file containing a list of expense objects."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"JSON file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if not isinstance(raw_data, list):
            raise ValueError("Expected JSON root to be a list of records.")

        imported = 0
        for item in raw_data:
            if isinstance(item, dict):
                try:
                    exp = Expense.from_dict(item)
                    self.add(exp)
                    imported += 1
                except (ValueError, TypeError):
                    continue
        return imported

    def export_to_json(self, filepath: Union[str, Path]) -> int:
        """Exports all expenses to formatted JSON."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        records = [exp.to_dict() for exp in self._expenses]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

        return len(records)

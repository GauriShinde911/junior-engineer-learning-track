"""
1.5 Strings & Files: CSV Report Generator
Demonstrates: csv module, pathlib.Path, file encoding, writing structured reports,
and non-crashing handling of missing or corrupted files.
"""

import csv
from pathlib import Path
from typing import Any, Dict, Optional, Union


def generate_sales_report(
    csv_filepath: Union[str, Path],
    report_filepath: Union[str, Path]
) -> Optional[Dict[str, Any]]:
    """
    Reads sales records from CSV (product_name, quantity, unit_price),
    computes revenue statistics, and exports a text summary report.
    Handles missing or invalid files gracefully without crashing.
    """
    in_path = Path(csv_filepath)
    out_path = Path(report_filepath)

    if not in_path.exists():
        print(f"[Warning] Input CSV does not exist: {in_path}")
        return None

    total_revenue = 0.0
    valid_rows = 0
    skipped_rows = 0
    best_seller = ""
    highest_quantity = 0

    try:
        with open(in_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)  # Consume optional header

            for line_no, row in enumerate(reader, start=2):
                if not row or len(row) < 3:
                    skipped_rows += 1
                    continue

                name = row[0].strip()
                try:
                    qty = int(row[1].strip())
                    price = float(row[2].strip())
                except ValueError:
                    # Skip rows with malformed numeric data
                    skipped_rows += 1
                    continue

                if qty <= 0 or price < 0:
                    skipped_rows += 1
                    continue

                valid_rows += 1
                revenue = qty * price
                total_revenue += revenue

                if qty > highest_quantity:
                    highest_quantity = qty
                    best_seller = name

    except (IOError, OSError) as err:
        print(f"[Error] Failed to read {in_path}: {err}")
        return None

    summary = {
        "valid_rows": valid_rows,
        "skipped_rows": skipped_rows,
        "total_revenue": round(total_revenue, 2),
        "best_seller": best_seller,
        "highest_quantity": highest_quantity
    }

    # Safe write using pathlib parent directory creation if necessary
    try:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        report_content = (
            "========================================\n"
            "       SALES PERFORMANCE REPORT        \n"
            "========================================\n"
            f"Input Source:       {in_path.name}\n"
            f"Valid Transactions: {valid_rows}\n"
            f"Skipped Rows:       {skipped_rows}\n"
            f"Total Revenue:      ${total_revenue:,.2f}\n"
            f"Top Product:        {best_seller or 'N/A'} ({highest_quantity} units sold)\n"
            "========================================\n"
        )
        out_path.write_text(report_content, encoding="utf-8")
    except (IOError, OSError) as err:
        print(f"[Error] Failed to write report to {out_path}: {err}")
        return None

    return summary


if __name__ == "__main__":
    sample_csv = Path("sample_data.csv")
    sample_report = Path("sales_report.txt")

    if not sample_csv.exists():
        sample_csv.write_text(
            "Product,Quantity,Price\n"
            "Laptop Stand,12,35.00\n"
            "Mechanical Keyboard,5,85.50\n"
            "Corrupt Row,invalid_number,40\n"
            "USB-C Cable,30,8.00\n",
            encoding="utf-8"
        )

    res = generate_sales_report(sample_csv, sample_report)
    print("Report Generation Result:", res)
    if sample_report.exists():
        print("\n" + sample_report.read_text(encoding="utf-8"))

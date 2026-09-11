"""
3.4 Excel Workbooks — build_excel_report.py

Produces a real .xlsx file with three sheets:
  1. "Raw Sales"    — the cleaned sales data
  2. "Monthly"      — the monthly summary table
  3. "Category Pivot" — revenue by category × month pivot

Formatting applied via openpyxl:
  - Bold, coloured header rows on every sheet
  - Auto-fit column widths (approximate)
  - Currency-style number format on revenue/price columns
  - Freeze top row (header) on every sheet

Run:
    python 03-pandas-excel/exercises/3.4-excel-workbooks/build_excel_report.py
"""

from pathlib import Path
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "03-pandas-excel" / "exercises" / "3.2-cleaning"))
sys.path.insert(0, str(SKILL_ROOT / "03-pandas-excel" / "exercises" / "3.3-transformations"))

from clean_messy_dataset import clean, RAW_FILE
from monthly_summary import build_monthly_summary
from cross_table_report import build_enriched, add_calculated_columns, build_pivot, load_products

OUTPUT_FILE = SKILL_ROOT / "03-pandas-excel" / "sample_data" / "sales_report.xlsx"

# ── Styling constants ─────────────────────────────────────────────────
HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
SUBHEADER_FILL = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
BODY_FONT = Font(size=10)
CURRENCY_FORMAT = '#,##0.00'
INT_FORMAT = '#,##0'

THIN_BORDER = Border(
    bottom=Side(style="thin", color="CCCCCC")
)


def style_header_row(ws, row: int, fill: PatternFill = HEADER_FILL) -> None:
    """Apply bold white-on-dark header styling to a given row."""
    for cell in ws[row]:
        cell.font = HEADER_FONT
        cell.fill = fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def autofit_columns(ws, min_width: int = 10, max_width: int = 40) -> None:
    """Approximate column width based on max content length."""
    for col in ws.columns:
        max_len = max((len(str(cell.value)) if cell.value else 0 for cell in col), default=0)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(min_width, min(max_len + 2, max_width))


def write_dataframe_to_sheet(ws, df: pd.DataFrame, currency_cols: list[str] | None = None) -> None:
    """Write a DataFrame to an openpyxl worksheet with headers and formatting."""
    currency_cols = currency_cols or []

    # Write header row
    for col_idx, col_name in enumerate(df.columns, start=1):
        ws.cell(row=1, column=col_idx, value=col_name)

    style_header_row(ws, 1)

    # Write data rows
    for row_idx, row_data in enumerate(df.itertuples(index=False), start=2):
        for col_idx, (col_name, value) in enumerate(zip(df.columns, row_data), start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            # Convert pandas Timestamp to Python datetime for Excel compatibility
            if hasattr(value, "isoformat"):
                cell.value = value.date() if hasattr(value, "date") else value
            elif hasattr(value, "item"):
                cell.value = value.item()  # numpy scalar → Python native
            else:
                cell.value = value

            # Apply currency format
            if col_name in currency_cols:
                cell.number_format = CURRENCY_FORMAT

            # Zebra striping
            if row_idx % 2 == 0:
                cell.fill = PatternFill(start_color="EBF2FA", end_color="EBF2FA", fill_type="solid")

    # Freeze header row
    ws.freeze_panes = "A2"

    # Auto-fit columns
    autofit_columns(ws)


def build_workbook(sales_df: pd.DataFrame, products_df: pd.DataFrame) -> Workbook:
    """Assemble the multi-sheet workbook and return it."""
    wb = Workbook()
    wb.remove(wb.active)  # Remove default empty sheet

    # ── Sheet 1: Raw Sales ────────────────────────────────────────────
    ws_raw = wb.create_sheet("Raw Sales")
    write_dataframe_to_sheet(
        ws_raw,
        sales_df,
        currency_cols=["unit_price", "revenue"]
    )

    # ── Sheet 2: Monthly Summary ──────────────────────────────────────
    ws_monthly = wb.create_sheet("Monthly")
    monthly = build_monthly_summary(sales_df)
    write_dataframe_to_sheet(
        ws_monthly,
        monthly,
        currency_cols=["total_revenue", "avg_order_value"]
    )

    # ── Sheet 3: Category × Month Pivot ──────────────────────────────
    ws_pivot = wb.create_sheet("Category Pivot")
    enriched = build_enriched(sales_df, products_df)
    enriched = add_calculated_columns(enriched)

    # Build category × month pivot
    enriched["month"] = pd.to_datetime(enriched["date"]).dt.to_period("M").astype(str)
    cat_pivot = pd.pivot_table(
        enriched,
        index="category",
        columns="month",
        values="revenue",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()
    cat_pivot.columns.name = None
    cat_pivot["TOTAL"] = cat_pivot.iloc[:, 1:].sum(axis=1)

    write_dataframe_to_sheet(
        ws_pivot,
        cat_pivot,
        currency_cols=list(cat_pivot.columns[1:])
    )

    return wb


if __name__ == "__main__":
    sales_df = clean(RAW_FILE)
    products_df = load_products()

    wb = build_workbook(sales_df, products_df)
    wb.save(OUTPUT_FILE)
    print(f"\n✓ Workbook written → {OUTPUT_FILE}")
    print(f"  Sheets: {wb.sheetnames}")

"""
3.3 Transformations — monthly_summary.py

Loads the cleaned sales data, adds a 'month' column, then uses
groupby + aggregate to produce a monthly summary table showing:
  - Total revenue per month
  - Number of orders per month
  - Average order value per month
  - Top-selling product per month

Run:
    python 03-pandas-excel/exercises/3.3-transformations/monthly_summary.py
"""

from pathlib import Path
import pandas as pd
import sys

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "03-pandas-excel" / "exercises" / "3.2-cleaning"))

# Use the cleaning pipeline so this script always works on fresh data
from clean_messy_dataset import clean, RAW_FILE


def build_monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups sales data by month and aggregates key metrics.

    Steps:
    1. Ensure 'date' is datetime and 'revenue' exists.
    2. Extract month period (YYYY-MM) as a string column.
    3. groupby('month') + agg() for total revenue, order count, avg value.
    4. Identify top-selling product per month via a separate groupby.
    5. Merge the two results.
    6. Sort by month ascending.
    """
    df = df.copy()

    # 1. Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # 2. Extract month string (YYYY-MM) for grouping
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # 3. Core aggregations
    summary = (
        df.groupby("month")
        .agg(
            total_revenue=("revenue", "sum"),
            order_count=("order_id", "nunique"),
            avg_order_value=("revenue", "mean"),
        )
        .round(2)
        .reset_index()
    )

    # 4. Top-selling product by revenue per month
    top_product = (
        df.groupby(["month", "product"])["revenue"]
        .sum()
        .reset_index()
        .sort_values(["month", "revenue"], ascending=[True, False])
        .drop_duplicates(subset="month", keep="first")
        .rename(columns={"product": "top_product", "revenue": "top_product_revenue"})
    )

    # 5. Merge
    summary = summary.merge(top_product[["month", "top_product"]], on="month", how="left")

    # 6. Sort
    summary = summary.sort_values("month").reset_index(drop=True)

    return summary


def print_summary(summary: pd.DataFrame) -> None:
    sep = "=" * 70
    print(f"\n{sep}")
    print("  MONTHLY SALES SUMMARY")
    print(sep)
    print(summary.to_string(index=False))
    print(sep)
    total = summary["total_revenue"].sum()
    print(f"\n  Grand total revenue: ₹{total:,.0f}")
    print(f"  Grand total orders : {summary['order_count'].sum()}\n")


if __name__ == "__main__":
    df = clean(RAW_FILE)
    summary = build_monthly_summary(df)
    print_summary(summary)

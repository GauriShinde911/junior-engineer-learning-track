"""
3.3 Transformations — cross_table_report.py

Demonstrates:
  1. merge() — joining sales data with the products reference table
  2. pivot_table() — reshaping data from rows to a matrix
  3. Calculated columns — margin % and revenue-per-unit

Run:
    python 03-pandas-excel/exercises/3.3-transformations/cross_table_report.py
"""

from pathlib import Path
import pandas as pd
import sys

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "03-pandas-excel" / "exercises" / "3.2-cleaning"))
from clean_messy_dataset import clean, RAW_FILE

PRODUCTS_FILE = SKILL_ROOT / "03-pandas-excel" / "sample_data" / "products.csv"


def load_products(path: Path = PRODUCTS_FILE) -> pd.DataFrame:
    return pd.read_csv(path)


def build_enriched(sales: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """
    LEFT JOIN sales onto products on the 'product' name column.
    Adds: supplier, product_id, reorder_level.
    Any sales row whose product has no match will have NaN in joined columns —
    a left join keeps all sales rows regardless.
    """
    enriched = sales.merge(products, on="product", how="left", suffixes=("", "_ref"))
    # Drop the duplicated category column that came from products
    if "category_ref" in enriched.columns:
        enriched = enriched.drop(columns=["category_ref"])
    return enriched


def add_calculated_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add two calculated columns:
      revenue_per_unit — revenue / qty (avg selling price including discounts)
      margin_pct       — synthetic margin: 30% for Electronics, 40% for Accessories,
                         35% for Furniture (illustrative, not real data)
    """
    df = df.copy()
    df["revenue_per_unit"] = (df["revenue"] / df["qty"]).round(2)

    margin_map = {"Electronics": 0.30, "Accessories": 0.40, "Furniture": 0.35}
    df["margin_pct"] = df["category"].map(margin_map).fillna(0.30)
    df["est_profit"] = (df["revenue"] * df["margin_pct"]).round(0).astype(int)
    return df


def build_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot table: rows = product, columns = month, values = total revenue.
    fill_value=0 so empty cells show 0 instead of NaN.
    """
    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    pivot = pd.pivot_table(
        df,
        index="product",
        columns="month",
        values="revenue",
        aggfunc="sum",
        fill_value=0,
    )
    pivot["TOTAL"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("TOTAL", ascending=False)
    return pivot


def build_category_region_pivot(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot: rows = category, columns = region, values = total revenue."""
    df = df.copy()
    pivot = pd.pivot_table(
        df,
        index="category",
        columns="region",
        values="revenue",
        aggfunc="sum",
        fill_value=0,
    )
    pivot["TOTAL"] = pivot.sum(axis=1)
    return pivot


if __name__ == "__main__":
    sales_df = clean(RAW_FILE)
    products_df = load_products()

    # 1. Enriched merge
    enriched = build_enriched(sales_df, products_df)
    enriched = add_calculated_columns(enriched)

    sep = "=" * 70
    print(f"\n{sep}")
    print("  ENRICHED SALES (LEFT JOIN with Products)")
    print(sep)
    display_cols = ["order_id", "product", "supplier", "qty", "revenue",
                    "revenue_per_unit", "margin_pct", "est_profit"]
    print(enriched[display_cols].to_string(index=False))

    # 2. Product × Month pivot
    pivot = build_pivot(enriched)
    print(f"\n{sep}")
    print("  PRODUCT × MONTH REVENUE PIVOT")
    print(sep)
    print(pivot.to_string())

    # 3. Category × Region pivot
    cat_region = build_category_region_pivot(enriched)
    print(f"\n{sep}")
    print("  CATEGORY × REGION REVENUE PIVOT")
    print(sep)
    print(cat_region.to_string())
    print()

"""
3.1 DataFrames — explore_dataset.py

Loads the sales_messy.csv sample file and demonstrates the core
DataFrame inspection methods: dtypes, shape, head/tail, describe,
value_counts, and selecting specific columns.

Run:
    python 03-pandas-excel/exercises/3.1-dataframes/explore_dataset.py
"""

from pathlib import Path
import pandas as pd

# ── Locate the sample data relative to this file ─────────────────────
SKILL_ROOT = Path(__file__).resolve().parents[3]  # junior-engineer-learning-track/
DATA_FILE = SKILL_ROOT / "03-pandas-excel" / "sample_data" / "sales_messy.csv"


def load_dataset(path: Path = DATA_FILE) -> pd.DataFrame:
    """Load the CSV file and return a DataFrame."""
    return pd.read_csv(path)


def explore(df: pd.DataFrame) -> None:
    """Print a structured exploration of the DataFrame."""

    sep = "=" * 55

    # 1. Shape
    print(sep)
    print("SHAPE (rows, columns):", df.shape)

    # 2. Column names + dtypes
    print(sep)
    print("COLUMNS & DTYPES:")
    print(df.dtypes.to_string())

    # 3. First 5 rows
    print(sep)
    print("HEAD (first 5 rows):")
    print(df.head().to_string(index=False))

    # 4. Last 5 rows
    print(sep)
    print("TAIL (last 5 rows):")
    print(df.tail().to_string(index=False))

    # 5. Numeric summary statistics
    print(sep)
    print("DESCRIBE (numeric columns):")
    print(df.describe().to_string())

    # 6. Column selection — scalar and multi-column
    print(sep)
    print("SINGLE COLUMN — product (Series):")
    print(df["product"].head(5).to_string())

    print(sep)
    print("MULTI-COLUMN SELECTION — order_id, product, unit_price:")
    print(df[["order_id", "product", "unit_price"]].head(5).to_string(index=False))

    # 7. Boolean indexing
    print(sep)
    print("FILTER — rows where unit_price > 10000:")
    expensive = df[df["unit_price"] > 10000]
    print(expensive[["order_id", "product", "unit_price"]].to_string(index=False))

    # 8. Value counts
    print(sep)
    print("VALUE COUNTS — product column:")
    print(df["product"].value_counts().to_string())

    # 9. Null counts per column
    print(sep)
    print("NULL COUNTS PER COLUMN:")
    print(df.isnull().sum().to_string())


if __name__ == "__main__":
    df = load_dataset()
    explore(df)

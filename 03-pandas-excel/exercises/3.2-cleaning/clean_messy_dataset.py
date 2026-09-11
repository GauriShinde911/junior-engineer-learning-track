"""
3.2 Cleaning — clean_messy_dataset.py

Takes sales_messy.csv (which has: duplicate rows, mixed date formats,
inconsistent category casing, missing qty and region values, a missing
sales_rep) and produces a clean, consistent DataFrame.

Every cleaning decision is documented in ASSUMPTIONS.md alongside this file.

Returns: a clean pd.DataFrame, also saves to sample_data/sales_clean.csv

Run:
    python 03-pandas-excel/exercises/3.2-cleaning/clean_messy_dataset.py
"""

from pathlib import Path
import pandas as pd

SKILL_ROOT = Path(__file__).resolve().parents[3]
RAW_FILE  = SKILL_ROOT / "03-pandas-excel" / "sample_data" / "sales_messy.csv"
OUT_FILE  = SKILL_ROOT / "03-pandas-excel" / "sample_data" / "sales_clean.csv"


# ── Individual cleaning steps (each step is a pure function) ──────────

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop exact duplicate rows (all columns identical).
    Keeps the first occurrence, drops subsequent ones.
    See ASSUMPTIONS.md §1.
    """
    before = len(df)
    df = df.drop_duplicates()
    dropped = before - len(df)
    if dropped:
        print(f"  [duplicates] Removed {dropped} duplicate row(s).")
    return df.reset_index(drop=True)


def parse_dates(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    """
    Normalise the date column to ISO format (YYYY-MM-DD).
    Uses pd.to_datetime with dayfirst=False and errors='coerce' so
    unparseable values become NaT (none exist in current sample, but
    the guard keeps the function safe for future data).
    See ASSUMPTIONS.md §2.
    """
    df = df.copy()
    df[col] = pd.to_datetime(df[col], format="mixed", errors="coerce")
    nat_count = df[col].isna().sum()
    if nat_count:
        print(f"  [dates] {nat_count} date(s) could not be parsed → set to NaT.")
    return df


def normalize_category(df: pd.DataFrame, col: str = "category") -> pd.DataFrame:
    """
    Title-case the category column so 'electronics', 'ELECTRONICS', and
    'Electronics' all become 'Electronics'.
    See ASSUMPTIONS.md §3.
    """
    df = df.copy()
    df[col] = df[col].str.strip().str.title()
    return df


def fill_missing_qty(df: pd.DataFrame, col: str = "qty") -> pd.DataFrame:
    """
    Convert qty to numeric (it was loaded as object due to mixed types).
    Rows where qty is missing are filled with 1 (minimum plausible order).
    See ASSUMPTIONS.md §4.
    """
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors="coerce")
    null_count = df[col].isna().sum()
    if null_count:
        print(f"  [qty] {null_count} missing value(s) filled with 1 (minimum order).")
        df[col] = df[col].fillna(1)
    df[col] = df[col].astype(int)
    return df


def fill_missing_region(df: pd.DataFrame, col: str = "region") -> pd.DataFrame:
    """
    Rows where region is NaN are labelled 'Unknown' rather than dropped —
    the order still has valid financial data.
    See ASSUMPTIONS.md §5.
    """
    df = df.copy()
    null_count = df[col].isna().sum()
    if null_count:
        print(f"  [region] {null_count} missing value(s) filled with 'Unknown'.")
        df[col] = df[col].fillna("Unknown")
    return df


def fill_missing_sales_rep(df: pd.DataFrame, col: str = "sales_rep") -> pd.DataFrame:
    """
    Rows where sales_rep is NaN are labelled 'Unassigned'.
    See ASSUMPTIONS.md §6.
    """
    df = df.copy()
    null_count = df[col].isna().sum()
    if null_count:
        print(f"  [sales_rep] {null_count} missing value(s) filled with 'Unassigned'.")
        df[col] = df[col].fillna("Unassigned")
    return df


def add_revenue_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive revenue = qty * unit_price as an integer column.
    This is only valid after qty is cleaned and cast to int.
    """
    df = df.copy()
    df["revenue"] = df["qty"] * df["unit_price"]
    return df


def clean(path: Path = RAW_FILE) -> pd.DataFrame:
    """
    Full cleaning pipeline.  Returns a clean DataFrame.
    """
    print(f"\nLoading: {path.name}")
    df = pd.read_csv(path)
    print(f"Raw shape: {df.shape}")

    print("\n--- Cleaning steps ---")
    df = remove_duplicates(df)
    df = parse_dates(df)
    df = normalize_category(df)
    df = fill_missing_qty(df)
    df = fill_missing_region(df)
    df = fill_missing_sales_rep(df)
    df = add_revenue_column(df)

    print(f"\nClean shape: {df.shape}")
    return df


if __name__ == "__main__":
    clean_df = clean()
    clean_df.to_csv(OUT_FILE, index=False, date_format="%Y-%m-%d")
    print(f"\nSaved clean file → {OUT_FILE.name}")
    print("\nSample output (first 5 rows):")
    print(clean_df.head().to_string(index=False))
    print("\nNull counts after cleaning:")
    print(clean_df.isnull().sum().to_string())
    print("\nData types after cleaning:")
    print(clean_df.dtypes.to_string())

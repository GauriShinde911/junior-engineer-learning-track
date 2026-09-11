"""
3.1 DataFrames — data_quality_report.py

Produces a structured data-quality report for any DataFrame:
  - Null count and null % per column
  - Inferred dtype per column
  - Duplicate row count (and optionally shows them)
  - Basic numeric stats (min, max, mean, std) for numeric columns
  - Unique value counts for low-cardinality (categorical) columns

Designed to be importable by other modules (report() returns a dict)
and runnable directly from the CLI.

Run:
    python 03-pandas-excel/exercises/3.1-dataframes/data_quality_report.py
"""

from pathlib import Path
from typing import Any
import pandas as pd

SKILL_ROOT = Path(__file__).resolve().parents[3]
DATA_FILE = SKILL_ROOT / "03-pandas-excel" / "sample_data" / "sales_messy.csv"
CARDINALITY_THRESHOLD = 15  # columns with ≤ this many unique values get a value_counts


def report(df: pd.DataFrame) -> dict[str, Any]:
    """
    Generate a quality report for a DataFrame.

    Returns a dict with keys:
      shape, null_summary, dtype_summary, duplicate_count,
      numeric_stats, categorical_summaries
    """
    total_rows, total_cols = df.shape

    # ── Null summary ──────────────────────────────────────────────────
    null_counts = df.isnull().sum()
    null_pct = (null_counts / total_rows * 100).round(1)
    null_summary = pd.DataFrame({
        "null_count": null_counts,
        "null_pct": null_pct,
        "dtype": df.dtypes
    })

    # ── Duplicate rows ────────────────────────────────────────────────
    dup_count = df.duplicated().sum()
    dup_rows = df[df.duplicated(keep=False)] if dup_count > 0 else pd.DataFrame()

    # ── Numeric stats ─────────────────────────────────────────────────
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    numeric_stats = df[numeric_cols].describe() if numeric_cols else pd.DataFrame()

    # ── Categorical value counts (low cardinality) ────────────────────
    categorical_summaries: dict[str, pd.Series] = {}
    for col in df.columns:
        if df[col].nunique() <= CARDINALITY_THRESHOLD:
            categorical_summaries[col] = df[col].value_counts(dropna=False)

    return {
        "shape": (total_rows, total_cols),
        "null_summary": null_summary,
        "duplicate_count": int(dup_count),
        "duplicate_rows": dup_rows,
        "numeric_stats": numeric_stats,
        "categorical_summaries": categorical_summaries,
    }


def print_report(df: pd.DataFrame, title: str = "DATA QUALITY REPORT") -> None:
    """Pretty-print the quality report to stdout."""
    r = report(df)
    sep = "=" * 60

    print(f"\n{sep}")
    print(f"  {title}")
    print(sep)
    print(f"  Rows: {r['shape'][0]}   Columns: {r['shape'][1]}")

    print(f"\n{'─' * 60}")
    print("  NULL COUNTS & DTYPES")
    print(f"{'─' * 60}")
    print(r["null_summary"].to_string())

    print(f"\n{'─' * 60}")
    print(f"  DUPLICATE ROWS: {r['duplicate_count']}")
    print(f"{'─' * 60}")
    if r["duplicate_count"] > 0:
        print(r["duplicate_rows"].to_string(index=False))
    else:
        print("  No duplicates found.")

    if not r["numeric_stats"].empty:
        print(f"\n{'─' * 60}")
        print("  NUMERIC COLUMN STATS")
        print(f"{'─' * 60}")
        print(r["numeric_stats"].to_string())

    if r["categorical_summaries"]:
        print(f"\n{'─' * 60}")
        print("  CATEGORICAL VALUE COUNTS (≤15 unique values)")
        print(f"{'─' * 60}")
        for col, counts in r["categorical_summaries"].items():
            print(f"\n  [{col}]")
            print(counts.to_string())

    print(f"\n{sep}\n")


if __name__ == "__main__":
    df = pd.read_csv(DATA_FILE)
    print_report(df)

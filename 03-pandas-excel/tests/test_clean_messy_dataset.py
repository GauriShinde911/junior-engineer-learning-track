"""Unit tests for 3.2 Cleaning (clean_messy_dataset)."""

import sys
from pathlib import Path
import pandas as pd

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "3.2-cleaning"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))

from clean_messy_dataset import clean, RAW_FILE


def test_clean_returns_dataframe():
    df = clean(RAW_FILE)
    assert isinstance(df, pd.DataFrame)
    required = [
        "order_id", "date", "product", "category", "qty",
        "unit_price", "region", "sales_rep", "revenue"
    ]
    for col in required:
        assert col in df.columns
    # No nulls in required columns after cleaning
    assert df[required].isnull().sum().sum() == 0
    # Revenue column is numeric and non-negative
    assert (df["revenue"] >= 0).all()
    # Duplicates removed
    assert df.duplicated().sum() == 0

"""Unit tests for 3.3 monthly_summary."""

import sys
from pathlib import Path
import pandas as pd

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "3.3-transformations"
CLEANING_DIR = MODULE_DIR / "exercises" / "3.2-cleaning"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))
sys.path.insert(0, str(CLEANING_DIR))

from monthly_summary import build_monthly_summary
from clean_messy_dataset import clean, RAW_FILE


def test_monthly_summary_structure():
    df_clean = clean(RAW_FILE)
    summary = build_monthly_summary(df_clean)
    expected_cols = {"month", "total_revenue", "order_count", "avg_order_value", "top_product"}
    assert set(summary.columns) == expected_cols
    assert not summary.empty
    for m in summary["month"]:
        assert isinstance(m, str) and len(m) == 7

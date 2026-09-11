"""Unit tests for 3.1 DataFrames (explore_dataset and data_quality_report)."""

import sys
from pathlib import Path
import pandas as pd

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "3.1-dataframes"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))

import explore_dataset
from data_quality_report import report


def test_load_and_explore():
    df = explore_dataset.load_dataset()
    assert not df.empty
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] > 0
    # ensure explore runs without error
    explore_dataset.explore(df)


def test_data_quality_report():
    df = explore_dataset.load_dataset()
    r = report(df)
    assert "shape" in r
    assert "null_summary" in r
    assert "duplicate_count" in r
    assert r["duplicate_count"] >= 1  # sales_messy has duplicate ORD-002

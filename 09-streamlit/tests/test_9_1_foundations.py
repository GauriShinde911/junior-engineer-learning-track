"""Unit tests for Exercise 9.1 pure-logic functions.

================================================================================
TESTING NOTE: STREAMLIT UI vs. PURE LOGIC
Streamlit apps render UI dynamically through its execution server and browser
websockets, which cannot be practically tested via headless standard pytest
without running full headless browser automation (Playwright/Selenium).
Therefore, professional Streamlit engineering extracts data loading, filtering,
KPI aggregation, and chart transformations into pure Python functions.
- COVERED BY TESTS: Data loading, multi-condition filtering, KPI mathematics,
  and chart table pivot transformations.
- NOT COVERED: Visual widget rendering (`st.title`, `st.metric`, `st.columns`).
================================================================================
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

exercise_dir = Path(__file__).resolve().parent.parent / "exercises" / "9.1-foundations"
sys.path.insert(0, str(exercise_dir))

from app import (
    load_data,
    filter_dataset,
    calculate_kpis,
    prepare_chart_data
)


@pytest.fixture
def sample_csv_path():
    return exercise_dir / "sample_data.csv"


@pytest.fixture
def sample_df(sample_csv_path):
    return load_data(sample_csv_path)


def test_load_data_returns_dataframe(sample_csv_path):
    """Verifies that load_data successfully loads the sample CSV."""
    df = load_data(sample_csv_path)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert list(df.columns) == ["department", "month", "revenue", "target", "satisfaction_score"]


def test_load_data_missing_file_raises():
    """Verifies that non-existent file path raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_data(Path("non_existent_data_file.csv"))


def test_filter_dataset_by_department(sample_df):
    """Verifies filtering by specific departments."""
    filtered = filter_dataset(sample_df, selected_departments=["Engineering"], min_revenue=0)
    assert set(filtered["department"].unique()) == {"Engineering"}
    assert len(filtered) == 3


def test_filter_dataset_by_revenue_threshold(sample_df):
    """Verifies filtering out rows below revenue threshold."""
    # Engineering Jan=45000, Feb=52000, Mar=61000; Marketing Jan=32000, Feb=34000, Mar=39000; Sales >=78000; Support <=25000
    filtered = filter_dataset(sample_df, selected_departments=[], min_revenue=50000)
    assert (filtered["revenue"] >= 50000).all()
    # Support has no rows >= 50000
    assert "Support" not in filtered["department"].values


def test_calculate_kpis_accuracy(sample_df):
    """Verifies mathematical correctness of KPI calculations."""
    kpis = calculate_kpis(sample_df)
    assert kpis["total_revenue"] == float(sample_df["revenue"].sum())
    assert kpis["total_target"] == float(sample_df["target"].sum())
    assert kpis["avg_satisfaction"] == round(float(sample_df["satisfaction_score"].mean()), 2)
    assert kpis["target_achievement_pct"] > 0


def test_calculate_kpis_empty_dataframe():
    """Verifies graceful zero-handling when filter yields no rows."""
    empty_df = pd.DataFrame(columns=["revenue", "target", "satisfaction_score"])
    kpis = calculate_kpis(empty_df)
    assert kpis["total_revenue"] == 0.0
    assert kpis["total_target"] == 0.0
    assert kpis["avg_satisfaction"] == 0.0
    assert kpis["target_achievement_pct"] == 0.0


def test_prepare_chart_data_pivot(sample_df):
    """Verifies pivot table formatting for multi-department chart rendering."""
    chart_df = prepare_chart_data(sample_df)
    assert isinstance(chart_df, pd.DataFrame)
    assert set(chart_df.columns) == {"Engineering", "Marketing", "Sales", "Support"}
    # Indexed by months Jan, Feb, Mar
    assert "Jan" in chart_df.index
    assert "Feb" in chart_df.index
    assert "Mar" in chart_df.index

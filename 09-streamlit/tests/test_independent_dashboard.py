"""Tests for pure data logic in independent/app.py."""

import importlib.util
from pathlib import Path
import pytest
import pandas as pd
from datetime import date

app_path = Path(__file__).resolve().parent.parent / "independent" / "app.py"
spec = importlib.util.spec_from_file_location("app_independent", str(app_path))
app_independent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_independent)

generate_sales_data = app_independent.generate_sales_data
filter_sales = app_independent.filter_sales
compute_kpis = app_independent.compute_kpis
revenue_by_category = app_independent.revenue_by_category
revenue_by_month = app_independent.revenue_by_month
segment_breakdown = app_independent.segment_breakdown
detect_anomalies = app_independent.detect_anomalies
top_transactions = app_independent.top_transactions
CATEGORIES = app_independent.CATEGORIES
REGIONS = app_independent.REGIONS
SEGMENTS = app_independent.SEGMENTS


@pytest.fixture(scope="module")
def full_df() -> pd.DataFrame:
    return generate_sales_data(n_rows=300)


class TestGenerateSalesData:
    def test_returns_dataframe(self, full_df):
        assert isinstance(full_df, pd.DataFrame)

    def test_correct_row_count(self, full_df):
        assert len(full_df) == 300

    def test_required_columns(self, full_df):
        assert {"date", "category", "region", "segment", "units", "unit_price", "revenue"}.issubset(full_df.columns)

    def test_all_categories_in_constants(self, full_df):
        assert set(full_df["category"].unique()).issubset(set(CATEGORIES))

    def test_all_regions_in_constants(self, full_df):
        assert set(full_df["region"].unique()).issubset(set(REGIONS))

    def test_revenue_is_positive(self, full_df):
        assert (full_df["revenue"] > 0).all()

    def test_is_reproducible(self):
        df1 = generate_sales_data(n_rows=50)
        df2 = generate_sales_data(n_rows=50)
        assert df1.equals(df2)


class TestFilterSales:
    def test_date_filter_excludes_out_of_range(self, full_df):
        start, end = date(2024, 3, 1), date(2024, 3, 31)
        result = filter_sales(full_df, start, end, CATEGORIES, REGIONS)
        assert (result["date"] >= start).all()
        assert (result["date"] <= end).all()

    def test_category_filter(self, full_df):
        result = filter_sales(full_df, date(2024, 1, 1), date(2024, 12, 31), ["Electronics"], REGIONS)
        assert (result["category"] == "Electronics").all()

    def test_region_filter(self, full_df):
        result = filter_sales(full_df, date(2024, 1, 1), date(2024, 12, 31), CATEGORIES, ["North"])
        assert (result["region"] == "North").all()

    def test_empty_category_list_returns_all(self, full_df):
        result = filter_sales(full_df, date(2024, 1, 1), date(2024, 12, 31), [], REGIONS)
        assert len(result) == len(full_df)

    def test_impossible_filter_returns_empty(self, full_df):
        result = filter_sales(full_df, date(2025, 1, 1), date(2025, 12, 31), CATEGORIES, REGIONS)
        assert result.empty


class TestComputeKpis:
    def test_all_keys_present(self, full_df):
        kpis = compute_kpis(full_df)
        assert {"total_revenue", "total_units", "avg_order_value", "n_transactions"}.issubset(kpis.keys())

    def test_empty_df_returns_zeros(self):
        empty = pd.DataFrame(columns=["revenue", "units"])
        kpis = compute_kpis(empty)
        assert kpis["total_revenue"] == 0.0
        assert kpis["total_units"] == 0
        assert kpis["n_transactions"] == 0

    def test_n_transactions_matches_len(self, full_df):
        kpis = compute_kpis(full_df)
        assert kpis["n_transactions"] == len(full_df)

    def test_total_revenue_matches_sum(self, full_df):
        kpis = compute_kpis(full_df)
        assert abs(kpis["total_revenue"] - round(full_df["revenue"].sum(), 2)) < 0.01


class TestRevenueByCategory:
    def test_returns_sorted_descending(self, full_df):
        result = revenue_by_category(full_df)
        revs = result["revenue"].tolist()
        assert revs == sorted(revs, reverse=True)

    def test_sum_matches_total(self, full_df):
        result = revenue_by_category(full_df)
        assert abs(result["revenue"].sum() - full_df["revenue"].sum()) < 0.01

    def test_empty_df_returns_empty(self):
        empty = pd.DataFrame(columns=["category", "revenue"])
        result = revenue_by_category(empty)
        assert result.empty


class TestRevenueByMonth:
    def test_returns_sorted_by_month(self, full_df):
        result = revenue_by_month(full_df)
        months = result["month"].tolist()
        assert months == sorted(months)

    def test_sum_matches_total(self, full_df):
        result = revenue_by_month(full_df)
        assert abs(result["revenue"].sum() - full_df["revenue"].sum()) < 0.01

    def test_empty_df(self):
        empty = pd.DataFrame(columns=["date", "revenue"])
        result = revenue_by_month(empty)
        assert result.empty


class TestSegmentBreakdown:
    def test_has_required_columns(self, full_df):
        result = segment_breakdown(full_df)
        assert {"segment", "revenue", "units", "revenue_pct"}.issubset(result.columns)

    def test_revenue_pct_sums_to_100(self, full_df):
        result = segment_breakdown(full_df)
        assert abs(result["revenue_pct"].sum() - 100.0) < 0.5  # rounding tolerance

    def test_sorted_descending(self, full_df):
        result = segment_breakdown(full_df)
        revs = result["revenue"].tolist()
        assert revs == sorted(revs, reverse=True)


class TestDetectAnomalies:
    def test_returns_required_columns(self, full_df):
        result = detect_anomalies(full_df)
        assert {"date", "daily_revenue", "is_anomaly"}.issubset(result.columns)

    def test_anomaly_column_is_bool(self, full_df):
        result = detect_anomalies(full_df)
        assert result["is_anomaly"].dtype == bool

    def test_high_threshold_produces_no_anomalies(self, full_df):
        result = detect_anomalies(full_df, threshold_std=100.0)
        assert not result["is_anomaly"].any()

    def test_low_threshold_produces_anomalies(self, full_df):
        result = detect_anomalies(full_df, threshold_std=0.01)
        assert result["is_anomaly"].any()

    def test_empty_df_returns_empty(self):
        empty = pd.DataFrame(columns=["date", "revenue"])
        result = detect_anomalies(empty)
        assert result.empty


class TestTopTransactions:
    def test_returns_n_rows(self, full_df):
        result = top_transactions(full_df, n=5)
        assert len(result) == 5

    def test_top_row_has_highest_revenue(self, full_df):
        result = top_transactions(full_df, n=1)
        assert result.iloc[0]["revenue"] == full_df["revenue"].max()

    def test_empty_df_returns_empty(self):
        empty = pd.DataFrame(columns=["date", "category", "region", "segment", "units", "revenue"])
        result = top_transactions(empty, n=5)
        assert result.empty

"""Tests for pure data logic in 9.4-data-ux/app.py.

Only tests functions that do not call st.* — UI is not directly testable.
"""

import importlib.util
from pathlib import Path
import pandas as pd
import pytest

app_path = Path(__file__).resolve().parent.parent / "exercises" / "9.4-data-ux" / "app.py"
spec = importlib.util.spec_from_file_location("app_9_4", str(app_path))
app_9_4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_9_4)

get_base_dataframe = app_9_4.get_base_dataframe
apply_filters = app_9_4.apply_filters
sort_by_severity = app_9_4.sort_by_severity
compute_summary_stats = app_9_4.compute_summary_stats
dataframe_to_csv_bytes = app_9_4.dataframe_to_csv_bytes
SEVERITY_ORDER = app_9_4.SEVERITY_ORDER


class TestGetBaseDataframe:
    def test_returns_dataframe(self):
        df = get_base_dataframe()
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        df = get_base_dataframe()
        assert {"id", "title", "team", "severity", "status", "reported_by"}.issubset(df.columns)

    def test_has_ten_rows(self):
        df = get_base_dataframe()
        assert len(df) == 10


class TestApplyFilters:
    @pytest.fixture
    def df(self):
        return get_base_dataframe()

    def test_empty_filters_return_all(self, df):
        # Empty lists mean no filter applied for that dimension
        result = apply_filters(df, [], [], [], "")
        assert len(result) == len(df)

    def test_team_filter(self, df):
        result = apply_filters(df, ["Frontend"], [], [], "")
        assert all(result["team"] == "Frontend")
        assert len(result) > 0

    def test_severity_filter(self, df):
        result = apply_filters(df, [], ["Critical"], [], "")
        assert all(result["severity"] == "Critical")

    def test_status_filter(self, df):
        result = apply_filters(df, [], [], ["Resolved"], "")
        assert all(result["status"] == "Resolved")

    def test_combined_filters(self, df):
        result = apply_filters(df, ["Backend"], ["High"], ["Open"], "")
        for _, row in result.iterrows():
            assert row["team"] == "Backend"
            assert row["severity"] == "High"
            assert row["status"] == "Open"

    def test_search_by_title(self, df):
        result = apply_filters(df, [], [], [], "timeout")
        assert any("timeout" in t.lower() for t in result["title"])

    def test_search_by_reporter(self, df):
        result = apply_filters(df, [], [], [], "Alice")
        assert all(result["reported_by"].str.lower().str.contains("alice"))

    def test_no_match_returns_empty_df(self, df):
        result = apply_filters(df, ["NonExistentTeam"], [], [], "")
        assert result.empty

    def test_case_insensitive_search(self, df):
        result_upper = apply_filters(df, [], [], [], "ALICE")
        result_lower = apply_filters(df, [], [], [], "alice")
        assert len(result_upper) == len(result_lower)


class TestSortBySeverity:
    @pytest.fixture
    def df(self):
        return get_base_dataframe()

    def test_first_row_is_critical_or_high_when_present(self, df):
        sorted_df = sort_by_severity(df)
        first_severity = sorted_df.iloc[0]["severity"]
        assert first_severity in ("Critical", "High")

    def test_severity_order_is_correct(self, df):
        sorted_df = sort_by_severity(df)
        orders = [SEVERITY_ORDER.get(s, 99) for s in sorted_df["severity"]]
        assert orders == sorted(orders)

    def test_empty_df_returns_empty(self):
        empty = pd.DataFrame(columns=["severity", "title"])
        result = sort_by_severity(empty)
        assert result.empty

    def test_does_not_drop_original_columns(self, df):
        sorted_df = sort_by_severity(df)
        assert "_sev_order" not in sorted_df.columns


class TestComputeSummaryStats:
    @pytest.fixture
    def df(self):
        return get_base_dataframe()

    def test_all_keys_present(self, df):
        stats = compute_summary_stats(df)
        assert {"total", "open", "critical", "resolved", "open_pct"}.issubset(stats.keys())

    def test_total_equals_df_len(self, df):
        stats = compute_summary_stats(df)
        assert stats["total"] == len(df)

    def test_empty_df_returns_zeros(self):
        empty = pd.DataFrame(columns=["status", "severity"])
        stats = compute_summary_stats(empty)
        assert stats["total"] == 0
        assert stats["open"] == 0
        assert stats["critical"] == 0
        assert stats["open_pct"] == 0.0

    def test_open_pct_is_percentage(self, df):
        stats = compute_summary_stats(df)
        assert 0.0 <= stats["open_pct"] <= 100.0

    def test_open_count_matches_manual(self, df):
        expected_open = int((df["status"] == "Open").sum())
        stats = compute_summary_stats(df)
        assert stats["open"] == expected_open


class TestDataframeToCsvBytes:
    @pytest.fixture
    def df(self):
        return get_base_dataframe()

    def test_returns_bytes(self, df):
        result = dataframe_to_csv_bytes(df)
        assert isinstance(result, bytes)

    def test_csv_is_decodable(self, df):
        raw = dataframe_to_csv_bytes(df).decode("utf-8")
        assert "id" in raw

    def test_csv_row_count_matches(self, df):
        import csv
        from io import StringIO
        raw = dataframe_to_csv_bytes(df).decode("utf-8")
        reader = list(csv.reader(StringIO(raw)))
        # 1 header + N data rows
        assert len(reader) == len(df) + 1

    def test_empty_df_produces_header_only_csv(self):
        empty = pd.DataFrame(columns=["id", "title", "team"])
        raw = dataframe_to_csv_bytes(empty).decode("utf-8")
        lines = [l for l in raw.splitlines() if l.strip()]
        assert len(lines) == 1  # header only

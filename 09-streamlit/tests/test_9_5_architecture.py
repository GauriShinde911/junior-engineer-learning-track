"""Tests for pure data logic in 9.5-architecture/app.py.

Does not test st.* decorated functions (cache wrappers) — those require a
running Streamlit server. Tests the underlying data transforms directly.
"""

import pytest
import pandas as pd
import math

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "exercises", "9.5-architecture"))

from app import (
    simulate_slow_data_fetch,
    compute_totals,
    compute_category_summary,
    get_top_n_products,
    compute_qoq_growth,
    validate_secrets_config,
)


class TestSimulateSlowDataFetch:
    def test_returns_dataframe(self):
        df = simulate_slow_data_fetch(delay_seconds=0)
        assert isinstance(df, pd.DataFrame)

    def test_has_required_columns(self):
        df = simulate_slow_data_fetch(delay_seconds=0)
        expected = {"product", "category", "q1_sales", "q2_sales", "q3_sales", "q4_sales"}
        assert expected.issubset(df.columns)

    def test_has_five_products(self):
        df = simulate_slow_data_fetch(delay_seconds=0)
        assert len(df) == 5


class TestComputeTotals:
    @pytest.fixture
    def df(self):
        return simulate_slow_data_fetch(delay_seconds=0)

    def test_adds_annual_total_column(self, df):
        result = compute_totals(df)
        assert "annual_total" in result.columns

    def test_annual_total_is_sum_of_quarters(self, df):
        result = compute_totals(df)
        for _, row in result.iterrows():
            expected = row["q1_sales"] + row["q2_sales"] + row["q3_sales"] + row["q4_sales"]
            assert row["annual_total"] == expected

    def test_does_not_modify_original(self, df):
        original_cols = list(df.columns)
        compute_totals(df)
        assert list(df.columns) == original_cols


class TestComputeCategorySummary:
    @pytest.fixture
    def df_totals(self):
        return compute_totals(simulate_slow_data_fetch(delay_seconds=0))

    def test_returns_dataframe(self, df_totals):
        result = compute_category_summary(df_totals)
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self, df_totals):
        result = compute_category_summary(df_totals)
        assert "category" in result.columns
        assert "category_total" in result.columns

    def test_sorted_descending(self, df_totals):
        result = compute_category_summary(df_totals)
        totals = result["category_total"].tolist()
        assert totals == sorted(totals, reverse=True)

    def test_sum_matches_overall_total(self, df_totals):
        result = compute_category_summary(df_totals)
        assert result["category_total"].sum() == df_totals["annual_total"].sum()


class TestGetTopNProducts:
    @pytest.fixture
    def df_totals(self):
        return compute_totals(simulate_slow_data_fetch(delay_seconds=0))

    def test_returns_n_rows(self, df_totals):
        for n in [1, 2, 3, 5]:
            result = get_top_n_products(df_totals, n=n)
            assert len(result) == n

    def test_top_product_has_highest_total(self, df_totals):
        result = get_top_n_products(df_totals, n=1)
        max_total = df_totals["annual_total"].max()
        assert result.iloc[0]["annual_total"] == max_total

    def test_returns_required_columns(self, df_totals):
        result = get_top_n_products(df_totals, n=3)
        assert {"product", "category", "annual_total"}.issubset(result.columns)


class TestComputeQoqGrowth:
    @pytest.fixture
    def df(self):
        return compute_totals(simulate_slow_data_fetch(delay_seconds=0))

    def test_adds_growth_columns(self, df):
        result = compute_qoq_growth(df)
        expected_new_cols = {"q2_growth_pct", "q3_growth_pct", "q4_growth_pct"}
        assert expected_new_cols.issubset(result.columns)

    def test_growth_calculation_is_correct(self, df):
        result = compute_qoq_growth(df)
        for _, row in result.iterrows():
            if row["q1_sales"] != 0:
                expected_q2_growth = round((row["q2_sales"] - row["q1_sales"]) / row["q1_sales"] * 100, 1)
                assert abs(row["q2_growth_pct"] - expected_q2_growth) < 0.001

    def test_does_not_modify_original(self, df):
        original_cols = list(df.columns)
        compute_qoq_growth(df)
        assert list(df.columns) == original_cols


class TestValidateSecretsConfig:
    def test_valid_config_passes(self):
        config = {"db_host": "localhost", "db_port": "5432", "api_key": "abc"}
        ok, missing = validate_secrets_config(config)
        assert ok is True
        assert missing == []

    def test_missing_key_fails(self):
        config = {"db_host": "localhost", "db_port": "5432"}  # missing api_key
        ok, missing = validate_secrets_config(config)
        assert ok is False
        assert "api_key" in missing

    def test_empty_string_value_fails(self):
        config = {"db_host": "localhost", "db_port": "5432", "api_key": ""}
        ok, missing = validate_secrets_config(config)
        assert ok is False
        assert "api_key" in missing

    def test_all_missing_returns_all_required(self):
        ok, missing = validate_secrets_config({})
        assert ok is False
        assert set(missing) == {"db_host", "db_port", "api_key"}

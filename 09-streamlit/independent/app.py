"""
Independent Project: Product Analytics Dashboard
=================================================
A full, independently runnable Streamlit analytics dashboard.

Features:
- Multi-tab layout (Overview, Sales Trends, Customer Segments, Alerts)
- Sidebar date-range and category filters
- KPI metric cards with delta values
- Filterable, downloadable tables
- Simulated real-time anomaly detection with alerts
- All data logic isolated for testability

Run:  streamlit run app.py
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


# ============================================================
# Data Generation & Pure Logic (Unit-Testable)
# ============================================================

CATEGORIES = ["Electronics", "Clothing", "Home & Garden", "Books", "Sports"]
REGIONS = ["North", "South", "East", "West"]
SEGMENTS = ["Enterprise", "SMB", "Consumer"]

RANDOM_SEED = 42


def generate_sales_data(n_rows: int = 300) -> pd.DataFrame:
    """Generate synthetic daily sales records."""
    rng = random.Random(RANDOM_SEED)
    start_date = date(2024, 1, 1)
    records = []
    for i in range(n_rows):
        sale_date = start_date + timedelta(days=rng.randint(0, 364))
        category = rng.choice(CATEGORIES)
        region = rng.choice(REGIONS)
        segment = rng.choice(SEGMENTS)
        units = rng.randint(1, 50)
        unit_price = round(rng.uniform(10.0, 500.0), 2)
        revenue = round(units * unit_price, 2)
        records.append({
            "date": sale_date,
            "category": category,
            "region": region,
            "segment": segment,
            "units": units,
            "unit_price": unit_price,
            "revenue": revenue,
        })
    return pd.DataFrame(records)


def filter_sales(
    df: pd.DataFrame,
    start: date,
    end: date,
    categories: List[str],
    regions: List[str],
) -> pd.DataFrame:
    """Apply date-range and multi-select filters to the sales DataFrame."""
    mask = (df["date"] >= start) & (df["date"] <= end)
    if categories:
        mask &= df["category"].isin(categories)
    if regions:
        mask &= df["region"].isin(regions)
    return df[mask].copy()


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute top-level KPIs from a filtered sales DataFrame."""
    if df.empty:
        return {"total_revenue": 0.0, "total_units": 0, "avg_order_value": 0.0, "n_transactions": 0}
    return {
        "total_revenue": round(df["revenue"].sum(), 2),
        "total_units": int(df["units"].sum()),
        "avg_order_value": round(df["revenue"].mean(), 2),
        "n_transactions": len(df),
    }


def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Group revenue by category, descending."""
    if df.empty:
        return pd.DataFrame(columns=["category", "revenue"])
    return (
        df.groupby("category")["revenue"]
        .sum()
        .reset_index()
        .sort_values("revenue", ascending=False)
        .reset_index(drop=True)
    )


def revenue_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate revenue by calendar month."""
    if df.empty:
        return pd.DataFrame(columns=["month", "revenue"])
    df = df.copy()
    df["month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)
    return (
        df.groupby("month")["revenue"]
        .sum()
        .reset_index()
        .sort_values("month")
        .reset_index(drop=True)
    )


def segment_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    """Compute revenue and unit share per customer segment."""
    if df.empty:
        return pd.DataFrame(columns=["segment", "revenue", "units", "revenue_pct"])
    agg = df.groupby("segment").agg(revenue=("revenue", "sum"), units=("units", "sum")).reset_index()
    total = agg["revenue"].sum()
    agg["revenue_pct"] = (agg["revenue"] / total * 100).round(1)
    return agg.sort_values("revenue", ascending=False).reset_index(drop=True)


def detect_anomalies(df: pd.DataFrame, threshold_std: float = 2.0) -> pd.DataFrame:
    """Flag daily revenue totals that exceed mean + threshold_std * std."""
    if df.empty:
        return pd.DataFrame(columns=["date", "daily_revenue", "is_anomaly"])
    daily = df.groupby("date")["revenue"].sum().reset_index()
    daily.columns = ["date", "daily_revenue"]
    mean = daily["daily_revenue"].mean()
    std = daily["daily_revenue"].std()
    daily["is_anomaly"] = daily["daily_revenue"] > (mean + threshold_std * std)
    return daily.sort_values("date").reset_index(drop=True)


def top_transactions(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top-N transactions by revenue."""
    if df.empty:
        return df
    return df.nlargest(n, "revenue")[["date", "category", "region", "segment", "units", "revenue"]]


# ============================================================
# Streamlit UI
# ============================================================

@st.cache_data
def load_data() -> pd.DataFrame:
    """Cached data load — runs once per session."""
    return generate_sales_data(n_rows=300)


def render_kpi_cards(kpis: Dict[str, Any], prev_kpis: Optional[Dict[str, Any]] = None) -> None:
    c1, c2, c3, c4 = st.columns(4)
    delta_rev = None if prev_kpis is None else round(kpis["total_revenue"] - prev_kpis["total_revenue"], 2)
    delta_units = None if prev_kpis is None else kpis["total_units"] - prev_kpis["total_units"]
    c1.metric("💰 Total Revenue", f"${kpis['total_revenue']:,.2f}", delta=f"${delta_rev:,.2f}" if delta_rev is not None else None)
    c2.metric("📦 Units Sold", f"{kpis['total_units']:,}", delta=str(delta_units) if delta_units is not None else None)
    c3.metric("🧾 Avg Order Value", f"${kpis['avg_order_value']:,.2f}")
    c4.metric("🔢 Transactions", kpis["n_transactions"])


def main() -> None:
    st.set_page_config(
        page_title="Product Analytics Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("📈 Product Analytics Dashboard")
    st.caption("Independent project: full analytics dashboard with filters, KPIs, trends, segments, and anomaly alerts.")

    df_all = load_data()

    # --------------------------------------------------------
    # Sidebar Filters
    # --------------------------------------------------------
    st.sidebar.header("🔽 Filters")

    min_date = df_all["date"].min()
    max_date = df_all["date"].max()
    start_date = st.sidebar.date_input("Start date", value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End date", value=max_date, min_value=min_date, max_value=max_date)

    if start_date > end_date:
        st.sidebar.error("Start date must be before end date.")
        return

    selected_categories = st.sidebar.multiselect("Category", options=CATEGORIES, default=CATEGORIES)
    selected_regions = st.sidebar.multiselect("Region", options=REGIONS, default=REGIONS)

    # --------------------------------------------------------
    # Filter Data
    # --------------------------------------------------------
    filtered = filter_sales(df_all, start_date, end_date, selected_categories, selected_regions)
    kpis = compute_kpis(filtered)

    if filtered.empty:
        st.warning("⚠️ No data matches the current filter selection. Adjust the sidebar filters.")
        return

    # --------------------------------------------------------
    # KPI Cards
    # --------------------------------------------------------
    render_kpi_cards(kpis)
    st.divider()

    # --------------------------------------------------------
    # Tabs
    # --------------------------------------------------------
    tab_overview, tab_trends, tab_segments, tab_alerts = st.tabs(
        ["📋 Overview", "📈 Trends", "👥 Segments", "🚨 Anomaly Alerts"]
    )

    with tab_overview:
        st.subheader("Revenue by Category")
        cat_df = revenue_by_category(filtered)
        st.dataframe(cat_df, use_container_width=True, hide_index=True)

        st.subheader("Top 10 Transactions")
        top_df = top_transactions(filtered, n=10)
        st.dataframe(top_df, use_container_width=True, hide_index=True)

        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered Data", data=csv, file_name="filtered_sales.csv", mime="text/csv")

    with tab_trends:
        st.subheader("Monthly Revenue Trend")
        monthly = revenue_by_month(filtered)
        if monthly.empty:
            st.info("No monthly data available for the selected filters.")
        else:
            st.line_chart(monthly.set_index("month")["revenue"])

        with st.expander("Monthly breakdown table"):
            st.dataframe(monthly, use_container_width=True, hide_index=True)

    with tab_segments:
        st.subheader("Customer Segment Breakdown")
        seg_df = segment_breakdown(filtered)
        left_col, right_col = st.columns([2, 1])
        left_col.dataframe(seg_df, use_container_width=True, hide_index=True)
        right_col.write("**Segment shares:**")
        for _, row in seg_df.iterrows():
            right_col.write(f"- **{row['segment']}**: {row['revenue_pct']}%")

    with tab_alerts:
        st.subheader("🚨 Daily Revenue Anomalies")
        anomaly_df = detect_anomalies(filtered, threshold_std=2.0)
        flagged = anomaly_df[anomaly_df["is_anomaly"]]

        if flagged.empty:
            st.success("✅ No anomalous daily revenue spikes detected in the selected range.")
        else:
            st.error(f"⚠️ {len(flagged)} anomalous day(s) detected (> mean + 2σ):")
            st.dataframe(flagged[["date", "daily_revenue"]], use_container_width=True, hide_index=True)

        with st.expander("Full daily revenue series"):
            st.dataframe(anomaly_df, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()

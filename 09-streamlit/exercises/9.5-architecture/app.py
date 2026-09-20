"""9.5 Architecture & Performance — Caching, Layout, and App Organization.

Covers: st.cache_data, st.cache_resource, st.columns/tabs/expander,
secrets management patterns, layout helpers, and performance profiling.
"""

import time
import hashlib
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st


# ==============================================================================
# Pure Logic (Testable Without Streamlit)
# ==============================================================================

def simulate_slow_data_fetch(delay_seconds: float = 0.0) -> pd.DataFrame:
    """
    Simulates a slow external data load (DB, API).
    In production this would be cached with @st.cache_data so the delay
    only happens once per session, not on every rerun.
    """
    if delay_seconds > 0:
        time.sleep(delay_seconds)
    return pd.DataFrame({
        "product": ["Widget A", "Widget B", "Widget C", "Widget D", "Widget E"],
        "category": ["Hardware", "Software", "Hardware", "Services", "Software"],
        "q1_sales": [12_000, 9_500, 7_800, 23_000, 4_100],
        "q2_sales": [14_500, 11_200, 6_300, 25_800, 5_900],
        "q3_sales": [11_000, 13_700, 8_200, 21_400, 7_600],
        "q4_sales": [16_000, 12_000, 9_100, 28_300, 8_200],
    })


def compute_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Adds an annual total column to the sales DataFrame."""
    df = df.copy()
    quarter_cols = [c for c in df.columns if c.endswith("_sales")]
    df["annual_total"] = df[quarter_cols].sum(axis=1)
    return df


def compute_category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates annual totals by product category."""
    if "annual_total" not in df.columns:
        df = compute_totals(df)
    return (
        df.groupby("category")["annual_total"]
        .sum()
        .reset_index()
        .rename(columns={"annual_total": "category_total"})
        .sort_values("category_total", ascending=False)
        .reset_index(drop=True)
    )


def get_top_n_products(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Returns the top-N products by annual_total."""
    if "annual_total" not in df.columns:
        df = compute_totals(df)
    return df.nlargest(n, "annual_total")[["product", "category", "annual_total"]]


def compute_qoq_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Computes quarter-over-quarter growth % per product."""
    df = df.copy()
    quarters = ["q1_sales", "q2_sales", "q3_sales", "q4_sales"]
    for i in range(1, len(quarters)):
        prev, curr = quarters[i - 1], quarters[i]
        col_name = f"{quarters[i].replace('_sales', '')}_growth_pct"
        df[col_name] = (
            ((df[curr] - df[prev]) / df[prev].replace(0, float("nan"))) * 100
        ).round(1)
    return df


def validate_secrets_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates that a secrets dict contains required keys.
    In a real app, these come from st.secrets or environment variables.
    """
    required_keys = ["db_host", "db_port", "api_key"]
    missing = [k for k in required_keys if k not in config or not config[k]]
    return (len(missing) == 0, missing)


# ==============================================================================
# Caching Wrappers (The cache decorators are the key Streamlit concept here)
# ==============================================================================

@st.cache_data(ttl=300)   # Cache data for 5 minutes; re-fetches after TTL
def load_sales_data() -> pd.DataFrame:
    """
    Cached data loader — decorated with @st.cache_data.
    Streamlit serialises the return value; called only on first run
    or after TTL expiry.
    """
    return simulate_slow_data_fetch(delay_seconds=0)   # delay=0 in tests/demo


@st.cache_resource  # Singleton — shared across all users/sessions (use for DB conns, ML models)
def get_shared_config() -> Dict[str, str]:
    """
    Cached resource — decorated with @st.cache_resource.
    Initialised once per app server start; not serialised.
    """
    return {
        "app_name": "Sales Performance Dashboard",
        "version": "1.0.0",
        "theme": "dark",
    }


# ==============================================================================
# UI Layer
# ==============================================================================

def main() -> None:
    st.set_page_config(
        page_title="Sales Performance Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    config = get_shared_config()
    st.title(f"📊 {config['app_name']}")
    st.caption("Demonstrates st.cache_data, st.cache_resource, tabs, columns, expanders.")

    # -------------------------------------------------------------------------
    # Load Data (cached)
    # -------------------------------------------------------------------------
    with st.spinner("Loading sales data..."):
        raw_df = load_sales_data()

    df_with_totals = compute_totals(raw_df)
    df_with_growth = compute_qoq_growth(df_with_totals)
    category_df = compute_category_summary(df_with_totals)
    top3 = get_top_n_products(df_with_totals, n=3)

    # -------------------------------------------------------------------------
    # Layout: 3-column summary cards
    # -------------------------------------------------------------------------
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", len(raw_df))
    c2.metric("Top Product", top3.iloc[0]["product"])
    c3.metric("Top Annual Total", f"${top3.iloc[0]['annual_total']:,}")

    st.divider()

    # -------------------------------------------------------------------------
    # Layout: Tabs for different views
    # -------------------------------------------------------------------------
    tab_overview, tab_growth, tab_category, tab_caching = st.tabs(
        ["📋 Overview", "📈 QoQ Growth", "🗂️ By Category", "⚡ Caching Info"]
    )

    with tab_overview:
        st.subheader("All Products — Annual Totals")
        st.dataframe(df_with_totals, use_container_width=True, hide_index=True)

        st.subheader("Top 3 Products")
        st.dataframe(top3, use_container_width=True, hide_index=True)

    with tab_growth:
        st.subheader("Quarter-over-Quarter Growth (%)")
        growth_cols = [c for c in df_with_growth.columns if c.endswith("_growth_pct")]
        display_cols = ["product"] + growth_cols
        st.dataframe(df_with_growth[display_cols], use_container_width=True, hide_index=True)
        st.info(
            "Positive growth % means sales increased vs prior quarter. "
            "NaN in Q1 growth_pct means there is no prior quarter to compare."
        )

    with tab_category:
        st.subheader("Sales by Category")
        col_left, col_right = st.columns([2, 1])
        col_left.dataframe(category_df, use_container_width=True, hide_index=True)
        col_right.write("**Category Breakdown**")
        for _, row in category_df.iterrows():
            col_right.write(f"- **{row['category']}**: ${row['category_total']:,}")

    with tab_caching:
        st.subheader("⚡ Caching Demo")
        st.write("""
        **`@st.cache_data`** is used on `load_sales_data()`.
        - Call it repeatedly — notice it returns instantly after the first call.
        - The return value is serialised (pickled), so it's safe for mutable data like DataFrames.
        - Use `ttl=300` to automatically expire the cache after 5 minutes.
        """)
        st.write("""
        **`@st.cache_resource`** is used on `get_shared_config()`.
        - Returns a **singleton** — the same object instance is shared across all sessions.
        - Use for database connections, ML models, or expensive startup resources.
        - Do NOT use for mutable data you want isolated per user.
        """)

        if st.button("⏱️ Time load_sales_data() with cache"):
            t0 = time.perf_counter()
            load_sales_data()
            elapsed = time.perf_counter() - t0
            st.success(f"Cached call returned in {elapsed*1000:.2f} ms (should be < 2 ms)")

        if st.button("🗑️ Clear data cache and re-time"):
            st.cache_data.clear()
            t0 = time.perf_counter()
            load_sales_data()
            elapsed = time.perf_counter() - t0
            st.warning(f"Cold call returned in {elapsed*1000:.2f} ms after cache clear")

    # -------------------------------------------------------------------------
    # Expander: Secrets/config reference
    # -------------------------------------------------------------------------
    st.divider()
    with st.expander("🔐 Secrets & Configuration Pattern", expanded=False):
        st.write(
            "In production, sensitive values come from `st.secrets` (`.streamlit/secrets.toml`) "
            "or environment variables — never hardcoded. Example:"
        )
        st.code(
            """# .streamlit/secrets.toml\n[database]\nhost = \"db.example.com\"\nport = 5432\npassword = \"...\"\n\n# Access in app:\nhost = st.secrets[\"database\"][\"host\"]""",
            language="toml"
        )
        ok, missing = validate_secrets_config({"db_host": "db.example.com", "db_port": "5432", "api_key": "abc"})
        if ok:
            st.success("✅ Example config is valid.")
        else:
            st.error(f"❌ Missing keys: {missing}")


if __name__ == "__main__":
    main()

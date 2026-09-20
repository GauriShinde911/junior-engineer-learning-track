"""9.1 Streamlit Foundations — Department Performance Dashboard.

================================================================================
STREAMLIT EXECUTION MODEL: RERUN-ON-INTERACTION
================================================================================
Streamlit executes Python scripts using a simple, declarative execution loop:
1. Top-to-Bottom Execution:
   Streamlit does not attach traditional async DOM event listeners. Instead,
   whenever a user interacts with ANY widget (selecting an item, dragging a slider,
   typing text), Streamlit immediately re-executes the ENTIRE script from line 1
   to the end.
2. Stateful Widget Values:
   During each rerun, widgets automatically return their latest user-selected
   value from the browser. Local Python variables not stored in `st.session_state`
   or cached via `@st.cache_data` are re-initialized from scratch.
3. Declarative UI Construction:
   Because the script runs sequentially on each interaction, code reading top-to-
   bottom mirrors the rendered visual structure of the web page.
================================================================================
"""

from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
import streamlit as st


# ==============================================================================
# Pure Data Logic Layer (Extracted for Isolated Unit Testing)
# ==============================================================================

def load_data(filepath: Path) -> pd.DataFrame:
    """Loads performance data from CSV file."""
    if not filepath.exists():
        raise FileNotFoundError(f"Data file not found at: {filepath}")
    return pd.read_csv(filepath)


def filter_dataset(
    df: pd.DataFrame,
    selected_departments: List[str],
    min_revenue: float
) -> pd.DataFrame:
    """Filters dataset by department membership and minimum revenue threshold."""
    filtered = df.copy()
    if selected_departments:
        filtered = filtered[filtered["department"].isin(selected_departments)]
    filtered = filtered[filtered["revenue"] >= min_revenue]
    return filtered


def calculate_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Computes summary metrics for display cards."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_target": 0.0,
            "avg_satisfaction": 0.0,
            "target_achievement_pct": 0.0
        }

    total_revenue = float(df["revenue"].sum())
    total_target = float(df["target"].sum())
    avg_satisfaction = float(df["satisfaction_score"].mean())
    achievement = (total_revenue / total_target * 100.0) if total_target > 0 else 0.0

    return {
        "total_revenue": total_revenue,
        "total_target": total_target,
        "avg_satisfaction": round(avg_satisfaction, 2),
        "target_achievement_pct": round(achievement, 1)
    }


def prepare_chart_data(df: pd.DataFrame) -> pd.DataFrame:
    """Pivots department revenue by month for bar/line chart rendering."""
    if df.empty:
        return pd.DataFrame()
    return df.pivot_table(
        index="month",
        columns="department",
        values="revenue",
        aggfunc="sum"
    ).fillna(0)


# ==============================================================================
# UI Presentation Layer
# ==============================================================================

def main() -> None:
    """Streamlit entry point for the Foundations exercise."""
    st.set_page_config(
        page_title="Department Performance Dashboard",
        page_icon="📊",
        layout="wide"
    )

    st.title("📊 Department Performance Viewer")
    st.caption("Demonstrates Streamlit widgets, layout columns, metrics, and reactive reruns.")

    # Load dataset
    data_path = Path(__file__).resolve().parent / "sample_data.csv"
    raw_df = load_data(data_path)

    # --------------------------------------------------------------------------
    # Layout Section 1: Sidebar Filter Widgets
    # --------------------------------------------------------------------------
    st.sidebar.header("Dashboard Filters")
    available_depts = sorted(raw_df["department"].unique().tolist())
    selected_depts = st.sidebar.multiselect(
        "Select Departments",
        options=available_depts,
        default=available_depts
    )

    min_rev_threshold = st.sidebar.slider(
        "Minimum Monthly Revenue ($)",
        min_value=0,
        max_value=100000,
        value=20000,
        step=5000
    )

    # Apply pure filtering logic
    filtered_df = filter_dataset(raw_df, selected_depts, min_rev_threshold)
    kpis = calculate_kpis(filtered_df)

    # --------------------------------------------------------------------------
    # Layout Section 2: Summary KPI Cards using st.columns
    # --------------------------------------------------------------------------
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"${kpis['total_revenue']:,.0f}")
    col2.metric("Target Goal", f"${kpis['total_target']:,.0f}")
    delta_target = kpis["target_achievement_pct"] - 100.0
    col3.metric("Goal Attainment", f"{kpis['target_achievement_pct']}%", delta=f"{delta_target:.1f}%")
    col4.metric("Avg Satisfaction", f"{kpis['avg_satisfaction']} / 5.0")

    st.divider()

    # --------------------------------------------------------------------------
    # Layout Section 3: Visual Chart & Detailed Table in Columns
    # --------------------------------------------------------------------------
    left_col, right_col = st.columns([3, 2])

    with left_col:
        st.subheader("Revenue by Department & Month")
        chart_data = prepare_chart_data(filtered_df)
        if not chart_data.empty:
            st.bar_chart(chart_data)
        else:
            st.info("No chart data available for current filter criteria.")

    with right_col:
        st.subheader("Filtered Records")
        st.dataframe(filtered_df, use_container_width=True)

    # --------------------------------------------------------------------------
    # Layout Section 4: Educational Note on Rerun Model
    # --------------------------------------------------------------------------
    with st.expander("ℹ️ How does Streamlit execute this code?"):
        st.markdown(
            """
            - Every time you adjust the **Department** selector or drag the **Revenue** slider,
              Streamlit **re-runs this entire Python file** from top to bottom.
            - `min_rev_threshold` immediately reflects the updated slider value.
            - `calculate_kpis()` and `prepare_chart_data()` are called again with the filtered data.
            - Streamlit intelligently diffs the rendered output to update the browser UI instantly.
            """
        )


if __name__ == "__main__":
    main()

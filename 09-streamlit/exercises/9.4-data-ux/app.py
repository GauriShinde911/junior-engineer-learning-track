"""9.4 Data UX — Filterable Report Table with Download and Status Messages.

Covers: filterable tables, st.dataframe, download buttons, status messages,
error handling, and explicit empty-state messages.
"""

from io import StringIO
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import streamlit as st


# ==============================================================================
# Pure Data Logic (Testable Without Streamlit)
# ==============================================================================

SAMPLE_RECORDS: List[Dict[str, Any]] = [
    {"id": "INC-001", "title": "Login page slow", "team": "Frontend", "severity": "Medium", "status": "Open", "reported_by": "Alice"},
    {"id": "INC-002", "title": "API timeout on /users", "team": "Backend", "severity": "High", "status": "In Progress", "reported_by": "Bob"},
    {"id": "INC-003", "title": "Broken CSV export", "team": "Frontend", "severity": "Low", "status": "Resolved", "reported_by": "Carol"},
    {"id": "INC-004", "title": "DB connection pool exhausted", "team": "Backend", "severity": "Critical", "status": "Open", "reported_by": "Dave"},
    {"id": "INC-005", "title": "Missing RBAC check on /admin", "team": "Security", "severity": "Critical", "status": "Open", "reported_by": "Eve"},
    {"id": "INC-006", "title": "Notification emails not sent", "team": "Backend", "severity": "Medium", "status": "In Progress", "reported_by": "Alice"},
    {"id": "INC-007", "title": "Dashboard chart rendering blank", "team": "Frontend", "severity": "Low", "status": "Resolved", "reported_by": "Frank"},
    {"id": "INC-008", "title": "TLS cert expiry alert failed", "team": "Security", "severity": "High", "status": "Resolved", "reported_by": "Grace"},
    {"id": "INC-009", "title": "Memory leak in worker process", "team": "Backend", "severity": "High", "status": "Open", "reported_by": "Hank"},
    {"id": "INC-010", "title": "Broken link in footer", "team": "Frontend", "severity": "Low", "status": "Open", "reported_by": "Ivy"},
]

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def get_base_dataframe() -> pd.DataFrame:
    """Returns the full incident records as a DataFrame."""
    return pd.DataFrame(SAMPLE_RECORDS)


def apply_filters(
    df: pd.DataFrame,
    teams: List[str],
    severities: List[str],
    statuses: List[str],
    search_text: str
) -> pd.DataFrame:
    """Applies multi-criteria filters to the DataFrame."""
    filtered = df.copy()

    if teams:
        filtered = filtered[filtered["team"].isin(teams)]
    if severities:
        filtered = filtered[filtered["severity"].isin(severities)]
    if statuses:
        filtered = filtered[filtered["status"].isin(statuses)]
    if search_text and search_text.strip():
        query = search_text.strip().lower()
        filtered = filtered[
            filtered["title"].str.lower().str.contains(query, na=False) |
            filtered["reported_by"].str.lower().str.contains(query, na=False)
        ]

    return filtered


def sort_by_severity(df: pd.DataFrame) -> pd.DataFrame:
    """Sorts incidents by severity (Critical → High → Medium → Low)."""
    if df.empty:
        return df
    df = df.copy()
    df["_sev_order"] = df["severity"].map(SEVERITY_ORDER).fillna(99)
    df = df.sort_values("_sev_order").drop(columns=["_sev_order"])
    return df


def compute_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes counts and percentages for dashboard cards."""
    total = len(df)
    if total == 0:
        return {"total": 0, "open": 0, "critical": 0, "resolved": 0, "open_pct": 0.0}
    open_count = int((df["status"] == "Open").sum())
    critical_count = int((df["severity"] == "Critical").sum())
    resolved_count = int((df["status"] == "Resolved").sum())
    return {
        "total": total,
        "open": open_count,
        "critical": critical_count,
        "resolved": resolved_count,
        "open_pct": round(open_count / total * 100, 1)
    }


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Serializes DataFrame to UTF-8 CSV bytes for download."""
    return df.to_csv(index=False).encode("utf-8")


# ==============================================================================
# UI Presentation Layer
# ==============================================================================

def main() -> None:
    st.set_page_config(
        page_title="Incident Report Viewer",
        page_icon="🔴",
        layout="wide"
    )

    st.title("🔴 Incident Report Viewer")
    st.caption(
        "Demonstrates filterable tables, download buttons, status messages, and empty-state handling."
    )

    base_df = get_base_dataframe()

    # -------------------------------------------------------------------------
    # Sidebar Filters
    # -------------------------------------------------------------------------
    st.sidebar.header("🔽 Filter Incidents")

    search = st.sidebar.text_input(
        "Search title or reporter",
        placeholder="e.g. Alice, timeout..."
    )

    all_teams = sorted(base_df["team"].unique().tolist())
    selected_teams = st.sidebar.multiselect(
        "Team", options=all_teams, default=all_teams
    )

    all_severities = ["Critical", "High", "Medium", "Low"]
    selected_severities = st.sidebar.multiselect(
        "Severity", options=all_severities, default=all_severities
    )

    all_statuses = sorted(base_df["status"].unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "Status", options=all_statuses, default=all_statuses
    )

    # -------------------------------------------------------------------------
    # Apply Filters
    # -------------------------------------------------------------------------
    filtered_df = apply_filters(
        base_df, selected_teams, selected_severities, selected_statuses, search
    )
    sorted_df = sort_by_severity(filtered_df)

    # -------------------------------------------------------------------------
    # Summary Metrics
    # -------------------------------------------------------------------------
    stats = compute_summary_stats(sorted_df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Shown", stats["total"])
    col2.metric("Open", stats["open"])
    col3.metric("Critical", stats["critical"])
    col4.metric("Resolved", stats["resolved"])

    st.divider()

    # -------------------------------------------------------------------------
    # Download Button
    # -------------------------------------------------------------------------
    csv_bytes = dataframe_to_csv_bytes(sorted_df)
    download_col, _ = st.columns([1, 4])
    download_col.download_button(
        label="⬇️ Download Filtered CSV",
        data=csv_bytes,
        file_name="incidents_filtered.csv",
        mime="text/csv",
        disabled=sorted_df.empty,
        use_container_width=True
    )

    # -------------------------------------------------------------------------
    # Filtered Table or Empty State
    # -------------------------------------------------------------------------
    if sorted_df.empty:
        # Explicit empty-state message — never leave a blank page
        st.warning(
            "⚠️ No incidents match the current filter criteria. "
            "Try adjusting the sidebar filters or clearing the search field."
        )
    else:
        st.subheader(f"Incidents ({len(sorted_df)} records)")
        st.dataframe(sorted_df, use_container_width=True, hide_index=True)

    # -------------------------------------------------------------------------
    # Simulated Action with Success/Error Status Messages
    # -------------------------------------------------------------------------
    st.divider()
    st.subheader("Quick Actions")

    action_col1, action_col2 = st.columns(2)

    if action_col1.button("✅ Mark All Shown as Reviewed", use_container_width=True):
        if sorted_df.empty:
            st.error("❌ No incidents to mark — apply filters that return records first.")
        else:
            st.success(f"✅ {len(sorted_df)} incident(s) successfully marked as reviewed.")

    if action_col2.button("📤 Simulate Submit Report", use_container_width=True):
        if stats["total"] == 0:
            st.error("❌ Cannot submit an empty report. Filters return no data.")
        else:
            st.success(
                f"📤 Report submitted: {stats['total']} incident(s), "
                f"{stats['critical']} critical, {stats['open']} open."
            )


if __name__ == "__main__":
    main()

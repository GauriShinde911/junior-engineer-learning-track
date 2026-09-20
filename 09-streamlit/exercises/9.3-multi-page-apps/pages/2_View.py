"""Page 2: View and Filter Tasks."""

import sys
from pathlib import Path
import streamlit as st

parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from components import (
    get_or_create_store,
    render_page_header,
    render_styled_table,
    render_task_summary_metrics
)

render_page_header("🔍 View & Filter Tasks", "Inspect tasks across priorities, statuses, and assignees.")

store = get_or_create_store()
df = store.to_dataframe()

render_task_summary_metrics(store)
st.write("")

if not df.empty:
    col1, col2 = st.columns(2)
    available_priorities = ["All"] + sorted(df["priority"].unique().tolist())
    selected_priority = col1.selectbox("Filter by Priority", options=available_priorities)

    available_statuses = ["All"] + sorted(df["status"].unique().tolist())
    selected_status = col2.selectbox("Filter by Status", options=available_statuses)

    filtered = df.copy()
    if selected_priority != "All":
        filtered = filtered[filtered["priority"] == selected_priority]
    if selected_status != "All":
        filtered = filtered[filtered["status"] == selected_status]

    render_styled_table(filtered)
else:
    st.info("No tasks exist in the store yet. Visit **1_Create** to add one.")

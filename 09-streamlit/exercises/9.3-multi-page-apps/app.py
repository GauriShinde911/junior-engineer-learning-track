"""9.3 Multi-page Apps — Home Entry Point.

Demonstrates Streamlit's `pages/` directory convention and shared `components.py`.
"""

import streamlit as st
from components import (
    get_or_create_store,
    render_page_header,
    render_task_summary_metrics,
    render_styled_table
)

st.set_page_config(
    page_title="Task Hub — Multi-Page App",
    page_icon="📋",
    layout="wide"
)

render_page_header(
    "📋 Team Task Hub (Home)",
    "Demonstrates Streamlit's multi-page application convention and cross-page session state."
)

store = get_or_create_store()

render_task_summary_metrics(store)
st.write("")

st.subheader("Current Active Tasks")
df = store.to_dataframe()
render_styled_table(df)

st.info(
    "💡 Use the **sidebar navigation** to visit **1_Create** to add tasks, "
    "**2_View** for detailed filtering, or **3_Delete** to remove tasks."
)

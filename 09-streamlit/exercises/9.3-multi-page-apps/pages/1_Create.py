"""Page 1: Create a New Task."""

import sys
from pathlib import Path
import streamlit as st

# Ensure parent directory is in sys.path for components import
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from components import get_or_create_store, render_page_header

render_page_header("➕ Create New Task", "Add a new task item into the shared session store.")

store = get_or_create_store()

with st.form("create_task_form", clear_on_submit=True):
    title = st.text_input("Task Title *", placeholder="e.g. Implement OAuth2 Refresh Token Flow")
    col1, col2 = st.columns(2)
    priority = col1.selectbox("Priority *", options=["Low", "Medium", "High", "Critical"], index=1)
    assignee = col2.text_input("Assignee *", placeholder="e.g. Alice")

    status = st.selectbox("Initial Status", options=["Pending", "In Progress", "Completed"])

    submitted = st.form_submit_button("Create Task ➔", use_container_width=True)

    if submitted:
        try:
            new_item = store.add_task(title, priority, assignee, status)
            st.success(f"Task **{new_item.id}** ('{new_item.title}') successfully created!")
        except ValueError as err:
            st.error(str(err))

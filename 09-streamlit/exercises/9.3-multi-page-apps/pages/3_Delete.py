"""Page 3: Delete a Task."""

import sys
from pathlib import Path
import streamlit as st

parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from components import get_or_create_store, render_page_header, render_styled_table

render_page_header("🗑️ Delete Task", "Safely remove a task from the system with confirmation.")

store = get_or_create_store()
tasks = store.get_all_tasks()

if not tasks:
    st.info("No tasks exist to delete.")
else:
    task_options = {f"{t.id} — {t.title} ({t.priority})": t.id for t in tasks}
    selected_label = st.selectbox("Select Task to Remove", options=list(task_options.keys()))
    selected_id = task_options[selected_label]
    target_task = store.get_task(selected_id)

    if target_task:
        with st.container(border=True):
            st.write(f"**ID:** {target_task.id}")
            st.write(f"**Title:** {target_task.title}")
            st.write(f"**Assignee:** {target_task.assignee}")
            st.write(f"**Status:** {target_task.status}")

        st.warning(f"⚠️ Are you sure you want to permanently delete **{target_task.id}**?")

        col1, col2 = st.columns([1, 4])
        confirm_delete = col1.button("Confirm Delete 🗑️", type="primary", use_container_width=True)

        if confirm_delete:
            deleted = store.delete_task(selected_id)
            if deleted:
                st.success(f"Task **{selected_id}** was permanently deleted.")
                st.rerun()
            else:
                st.error("Failed to delete task.")

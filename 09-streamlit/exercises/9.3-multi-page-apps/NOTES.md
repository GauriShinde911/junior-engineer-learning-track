# 9.3 Multi-page Apps — Concepts & Reference

## Core Concepts
Streamlit simplifies large application architectures through its filesystem-based multi-page convention. By organizing scripts inside a `pages/` directory alongside the entry file, Streamlit automatically provisions responsive sidebar navigation without third-party routing libraries.

## Multi-Page Architecture & Conventions
- **Filesystem Routing**: Streamlit scans the `pages/` directory relative to the root `app.py`. Filenames prefixed with numbers (e.g. `1_Create.py`, `2_View.py`, `3_Delete.py`) define both the sidebar ordering and clean URL slugs.
- **Shared Session State**: `st.session_state` is preserved across page switches. Any object stored in session state during page 1 remains accessible and mutable on page 2 and page 3.
- **Component Factoring**: Avoid duplicating UI widgets or data logic across pages. Extract common patterns (headers, tables, dialogs, data stores) into a shared module like `components.py` and import them across pages.

## Key Concepts Used
- `pages/` directory: Streamlit's built-in convention for declaring sub-pages.
- File prefixes (`1_...`, `2_...`): Automatically sets sidebar display order and cleans up labels.
- `st.session_state.task_store`: Acts as the unified, shared in-memory data store across page navigations.
- Reusable UI functions: Modular layout helpers (`render_page_header`, `render_task_summary_metrics`, `render_styled_table`).

## Applied Implementation in this Folder
In [`09-streamlit/exercises/9.3-multi-page-apps/`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.3-multi-page-apps/), [`app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.3-multi-page-apps/app.py) serves as the Home dashboard. The `pages/` directory hosts `1_Create.py`, `2_View.py`, and `3_Delete.py` for full CRUD operations. All pages share the `TaskStore` and UI components defined in [`components.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.3-multi-page-apps/components.py).

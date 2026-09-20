# 9.4 Data UX — Concepts & Reference

## Core Concepts
A professional data dashboard must do more than display a table. It needs robust UX patterns: filters that narrow records predictably, clear feedback when actions succeed or fail, an explicit message when filtered results are empty, and a download path for offline analysis.

## Key UX Patterns

### Filterable Tables
`st.dataframe()` renders interactive, sortable, scrollable tables with built-in column resizing. Filters are implemented as sidebar widgets (`st.multiselect`, `st.text_input`) whose values are applied to a pandas DataFrame before rendering. Each filter interaction triggers a rerun that immediately updates the table.

### Download Buttons
`st.download_button()` converts in-memory data (bytes, strings) into a browser-initiated file download with a single click. No server-side temporary file is written. When the filtered result is empty, the button is visually disabled (`disabled=True`) to prevent downloading zero-row files.

### Status Messages (Success / Error)
`st.success()`, `st.error()`, `st.warning()`, and `st.info()` render color-coded notification banners. They are rendered conditionally after user actions and disappear on the next rerun if the triggering condition no longer holds — keeping the UI clean.

### Empty-State Messages
When filters return zero results, never leave a blank white space. An explicit `st.warning()` or `st.info()` banner explains why the table is empty and what the user can do to recover. This is a key data UX best practice.

## Key Functions Used
- `st.multiselect(options, default)`: Multi-select filter widget preserving all selected options.
- `st.dataframe(df, hide_index=True)`: Sortable, scrollable interactive table.
- `st.download_button(label, data, file_name, mime)`: Browser download for filtered CSV exports.
- `st.success()` / `st.error()` / `st.warning()`: Actionable user feedback banners.

## Applied Implementation in this Folder
In [`app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.4-data-ux/app.py), incident data is filtered across team, severity, and status dimensions. A CSV download button exports the filtered view. Empty filters display a clear recovery hint, and action buttons produce explicit success/error feedback.

# 9.1 Streamlit Foundations — Concepts & Reference

## Core Concepts
Streamlit enables Python developers to construct data dashboards and interactive tools purely in Python, without writing HTML, CSS, or JavaScript. Its fundamental design model is declarative and reactive: you write Python code top-to-bottom, and Streamlit translates that script into an interactive web interface.

## The Rerun Execution Model
- **Why Whole-Script Reruns Occur**: Conventional web frameworks use complex state trees and event listeners. In Streamlit, any user interaction with a widget (changing a slider, clicking a checkbox) triggers a complete re-execution of the Python script from line 1.
- **Benefits**: Simplifies code flow—variables directly reflect the latest widget state without callback wiring or manual DOM manipulation.
- **Engineering Consideration**: Computationally heavy operations (e.g. training a model, querying remote databases) should not rerun on every tick; they must be cached using `@st.cache_data` or managed via `st.session_state`.

## Key Functions Used
- `st.set_page_config(layout="wide")`: Configures page title, icon, and wide responsive layout mode.
- `st.columns([col_widths])`: Organizes the page into responsive horizontal side-by-side containers.
- `st.metric(label, value, delta)`: Formats high-level KPI cards with optional trend indicators.
- `st.dataframe(df)`: Displays interactive, sortable data tables from pandas DataFrames.
- `st.bar_chart(df)`: Renders responsive charts without requiring separate charting configuration.

## Applied Implementation in this Folder
In [`app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.1-foundations/app.py), departmental revenue data from [`sample_data.csv`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.1-foundations/sample_data.csv) is displayed using responsive columns, metric cards, a filtered table, and a multi-department bar chart. Pure calculation logic (`calculate_kpis`, `filter_dataset`) is isolated from UI presentation for unit testing.

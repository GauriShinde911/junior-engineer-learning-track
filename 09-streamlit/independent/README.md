# Independent Project: Product Analytics Dashboard

## Project Overview
A full-featured product analytics dashboard that combines every Streamlit concept from sections 9.1–9.5 into a single, independently runnable application.

## How to Run
```bash
cd 09-streamlit/independent
streamlit run app.py
```

## Features Built
| Feature | Streamlit API Used |
|---|---|
| Date-range + multi-select sidebar filters | `st.sidebar.date_input`, `st.sidebar.multiselect` |
| KPI metric cards with delta indicators | `st.metric()` with `delta=` |
| Tabbed navigation | `st.tabs()` |
| Filterable, downloadable table | `st.dataframe()`, `st.download_button()` |
| Line chart for monthly trends | `st.line_chart()` |
| Collapsible detail section | `st.expander()` |
| Empty-state and error messages | `st.warning()`, `st.error()`, `st.success()` |
| Cached data load | `@st.cache_data` |

## Data & Logic Architecture
All business logic is isolated in pure functions at the top of `app.py` — testable without Streamlit:

| Function | Purpose |
|---|---|
| `generate_sales_data(n)` | Creates 300 synthetic sales records with seed for reproducibility |
| `filter_sales(df, start, end, cats, regions)` | Applies date + category + region filters |
| `compute_kpis(df)` | Returns revenue, units, avg order value, transaction count |
| `revenue_by_category(df)` | Groups and ranks revenue by product category |
| `revenue_by_month(df)` | Aggregates revenue into monthly periods for trend chart |
| `segment_breakdown(df)` | Revenue + units + share % per customer segment |
| `detect_anomalies(df, std)` | Flags daily revenue outliers beyond mean + N×std |
| `top_transactions(df, n)` | Returns top-N rows by revenue |

## What This Project Demonstrates
- **Real separation of concerns**: data generation, filter logic, and aggregations are all in pure functions; the UI layer only renders their outputs.
- **Progressive complexity**: sidebar controls affect every tab simultaneously through a single `filter_sales()` call before the tab split.
- **Graceful degradation**: every empty-state path is explicitly handled — if filters produce zero rows, a recovery message is shown immediately and the tabs are never rendered on empty data.
- **Anomaly alerting**: statistical outlier detection (mean + 2σ) is implemented as a pure function and surfaced in a dedicated Alerts tab.

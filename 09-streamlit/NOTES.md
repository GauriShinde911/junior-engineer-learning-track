# Streamlit Dashboard Development — Skill Overview

Streamlit enables engineers to turn data scripts into shareable, interactive web applications in pure Python without writing boilerplate HTML, CSS, or JavaScript. However, building production-grade Streamlit applications requires a solid grasp of its reactive execution model, state management, caching mechanics, and design patterns for testability.

This module walks through Streamlit from core foundations to advanced multi-page architectures, data UX patterns, performance optimization, and a full independent product analytics dashboard.

---

## Module Roadmap & Curriculum Index

| Subsection | Focus Area | One-Line Summary | Reference Guide |
|---|---|---|---|
| **9.1** | **Foundations & Rerun Model** | Understands the top-to-bottom rerun execution model, basic inputs/widgets, and layout containers. | [9.1 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.1-foundations/NOTES.md) |
| **9.2** | **Forms & State Management** | Uses `st.session_state` for multi-step wizards, preserving state across reruns, and form batching with `st.form`. | [9.2 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.2-forms-state/NOTES.md) |
| **9.3** | **Multi-Page Applications** | Builds multi-page applications using the `pages/` directory convention and reusable shared component layers. | [9.3 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.3-multi-page-apps/NOTES.md) |
| **9.4** | **Data UX & Feedback** | Delivers filterable data tables, in-memory CSV downloads, action alerts, and explicit empty-state handling. | [9.4 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.4-data-ux/NOTES.md) |
| **9.5** | **Architecture & Performance** | Optimizes apps using `@st.cache_data`, `@st.cache_resource`, responsive column/tab/expander layouts, and secrets management. | [9.5 NOTES.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.5-architecture/NOTES.md) |
| **Independent** | **Product Analytics Dashboard** | Production-ready analytics dashboard with date filters, KPI metrics, monthly trends, segment splits, and anomaly alerts. | [Independent README.md](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/independent/README.md) |

---

## Core Streamlit Architectural Principles

### 1. The Reactive Rerun Model
Streamlit executes Python scripts from top to bottom on every user interaction (button click, slider move, text input).
- Any local variables created during a run are discarded when the script finishes.
- Heavy computations outside caching decorators will re-execute on every interaction, causing noticeable latency.

### 2. Session State Persistence (`st.session_state`)
To keep data alive across reruns or across different pages in a multi-page app, store it in `st.session_state`:
```python
if "user_tasks" not in st.session_state:
    st.session_state.user_tasks = []
```
- Initialize session keys defensively using the `if "key" not in st.session_state:` pattern.
- State persists across page transitions in multi-page applications as long as the browser tab stays open.

### 3. Separation of Logic and UI for Testability
Streamlit UI functions (`st.write`, `st.button`, `st.dataframe`) cannot be directly executed in standard unit tests without a running Streamlit runtime.
- **Best Practice**: Isolate business logic, data generation, filtering, and aggregation into pure functions or domain classes that return standard Python types or pandas DataFrames.
- Test pure functions thoroughly with `pytest`, keeping Streamlit code as a lightweight presentation layer.

### 4. Caching Strategies: Data vs. Resources
- **`@st.cache_data`**: Used for functions that return serializable data (DataFrames, dicts, arrays, text). Copies the returned object to ensure safe mutation without side effects. Supports `ttl` for automatic cache invalidation.
- **`@st.cache_resource`**: Used for non-serializable or singleton objects (database connections, ML models, network clients). Returns the exact same object reference to all users/sessions.

### 5. Defensive UX and Empty-State Handling
- Never present users with empty screens or raw tracebacks when filters yield zero rows.
- Provide clear explanatory banners (`st.warning`, `st.info`) explaining what happened and how to recover (e.g., widening filter parameters).
- Disable action buttons (such as file downloads or batch operations) when dataset selections are empty (`disabled=True`).

### 6. Secrets & Environment Configuration
- Never commit credentials, passwords, or API keys into git repositories.
- Use `.streamlit/secrets.toml` during local development (and add `.streamlit/secrets.toml` to `.gitignore`).
- Access secrets via `st.secrets["key"]` or standard environment variables.

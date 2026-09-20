# 9.5 Architecture & Performance — Concepts & Reference

## Core Concepts
When a Streamlit app grows beyond a single page, three concerns become critical: performance (avoid redundant computation), layout (guide the user's eye), and secrets management (never commit credentials).

## Caching Deep Dive

### `@st.cache_data`
- **Use for**: Any function that loads or transforms data (DataFrames, JSON, file reads, API calls).
- **How it works**: Streamlit serialises (pickles) the return value. Each unique set of arguments gets its own cache entry.
- **Persistence**: Survives reruns within the same session. Cleared with `st.cache_data.clear()` or via the triple-dot menu.
- **`ttl` parameter**: `ttl=300` means the cache expires after 5 minutes and the next call re-fetches fresh data.

```python
@st.cache_data(ttl=300)
def load_data_from_db(query: str) -> pd.DataFrame:
    return pd.read_sql(query, engine)
```

### `@st.cache_resource`
- **Use for**: Singleton objects: database connections, ML models, HTTP session pools.
- **How it works**: Returns the **same object instance** to all sessions/users. Not serialised.
- **Critical difference**: If the cached object is mutated, all users see the mutation.

```python
@st.cache_resource
def get_db_engine():
    return create_engine(st.secrets["database"]["url"])
```

## Layout Elements

| Widget | Purpose |
|---|---|
| `st.columns(n)` | Side-by-side layout; returns list of column contexts |
| `st.tabs(labels)` | Tabbed view; content in `with tab:` blocks |
| `st.expander(label)` | Collapsible section; reduces visual clutter |
| `st.sidebar.*` | Left sidebar persistent controls |
| `st.divider()` | Horizontal separator for visual rhythm |

## Secrets Management Pattern
- Store secrets in `.streamlit/secrets.toml` (gitignored) during development.
- In production (Streamlit Cloud), set secrets via the web UI.
- Access with `st.secrets["section"]["key"]` — raises `KeyError` if missing.
- **Never** hardcode passwords, API keys, or tokens in app source code.

## App Organisation Best Practices
- Keep pure logic in separate modules (`data.py`, `transforms.py`) — testable without Streamlit.
- Keep UI wiring in `app.py` — thin; imports from logic modules.
- Use `pages/` directory for multi-page apps (prefix filenames with numbers for ordering).
- Centralise shared state in `st.session_state` at the top of `app.py`.

## Applied Implementation in this Folder
[`app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.5-architecture/app.py) demonstrates `@st.cache_data` on the data loader, `@st.cache_resource` for a shared config singleton, tabbed navigation across four views, a 3-column metric summary, and an expander showing the secrets config pattern.

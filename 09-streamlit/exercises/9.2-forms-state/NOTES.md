# 9.2 Forms & State Management — Concepts & Reference

## Core Concepts
Because Streamlit re-executes scripts from top to bottom on user input, local variables do not survive between interactions. Building robust workflows requires two core primitives: `st.session_state` to retain data across reruns, and `st.form` to batch user inputs atomically.

## Why Forms and Session State Matter
- **Input Batching with `st.form`**: Without a form, typing a single character into `st.text_input` or selecting a dropdown item immediately re-runs the entire application. An `st.form` suppresses script execution until the user clicks `st.form_submit_button`, providing a cohesive and responsive data-entry experience.
- **State Persistence with `st.session_state`**: Acts as a dictionary tied to the user's browser session. It allows multi-step wizards, authentication tokens, and user shopping carts to survive across multiple page reruns.
- **Callbacks (`on_click`, `on_change`)**: Run immediately before the rest of the script is executed, making them ideal for atomic data mutations, state transitions, or clearing form caches.

## Key Functions Used
- `st.session_state[key]`: Reads and writes session-persisted variables that survive script reruns.
- `with st.form(key)`: Defines an isolated input container that batches widget interactions.
- `st.form_submit_button(label)`: The mandatory button inside a form that triggers validation and rerun.
- `st.rerun()`: Explicitly requests a script re-execution to render updated UI state immediately.
- `st.progress(pct)`: Renders visual step-completion indicators across multi-page workflows.

## Applied Implementation in this Folder
In [`app.py`](file:///C:/Users/Admin/.gemini/antigravity-ide/scratch/junior-engineer-learning-track/09-streamlit/exercises/9.2-forms-state/app.py), `RegistrationWizard` models a 3-step asset registration state machine. User data from Step 1 persists into Step 2 inside `st.session_state.wizard`, using `st.form` for validation before completing registration and presenting the summary in Step 3.

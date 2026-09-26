# 11.3 External Configuration for Packaged Apps

## Core Concept
Once Python code is bundled by PyInstaller, the bundle is read-only — the .exe and its
internal `.pyc` files cannot be edited without rebuilding. Any configuration that might
need to change after deployment (output paths, feature flags, log levels, API endpoints)
must live **outside** the bundle, in a writable directory that persists across reinstalls.

## Why Hardcoded Config Breaks Packaged Apps
In `app_with_bad_config.py`, values like `OUTPUT_DIR` and `MAX_RESULTS` are compiled into
the bytecode inside the bundle. To change any setting, a developer must:
1. Edit the source file.
2. Re-run PyInstaller.
3. Re-distribute the new exe to every user.

For anything that varies per environment or per deployment, this makes routine operational
changes into a full release cycle.

## The Correct Pattern — `app_with_external_config.py`
- Config lives in a JSON file at a **writable, well-known path** outside the bundle.
- The app searches for it at startup in priority order: beside the exe first, then
  `%APPDATA%\\AppName\\config.json` for per-user settings.
- If the file is missing, the app exits immediately with a **clear, actionable error message**
  telling the user exactly where to create it — not a cryptic Python traceback.
- File values are merged over hardcoded defaults, so the config file only needs to contain
  the values the operator wants to override.

## Key Windows Config Directories
| Path | Scope | Writable By |
|---|---|---|
| Beside the exe | Per-install | Whoever owns the install directory |
| `%APPDATA%\AppName\` | Per-user | The logged-in user |
| `%PROGRAMDATA%\AppName\` | Machine-wide | Administrators |

## `sys.frozen` and `sys._MEIPASS`
- `sys.frozen` is `True` when running inside a PyInstaller bundle; `False` in normal dev mode.
- Use `sys.executable` (not `__file__`) to locate the exe directory inside a frozen app.
- These attributes let you write path-resolution logic that works correctly in both dev and
  packaged modes.

## Connection to Exercises
`app_with_bad_config.py` and `app_with_external_config.py` show the same word-count feature
with and without the correct config pattern. Automated tests in
`tests/test_11_3_configuration.py` verify the config-loading logic: that external config is
read, merged correctly, and that a missing config file produces a clean SystemExit.

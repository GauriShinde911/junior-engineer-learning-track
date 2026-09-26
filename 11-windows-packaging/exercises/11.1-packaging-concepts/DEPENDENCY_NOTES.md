# Dependency & Packaging Notes: `sample_cli.py`

## What `sample_cli.py` Depends On

`sample_cli.py` uses **only the Python standard library**:

| Module | Purpose |
|---|---|
| `argparse` | Parses command-line flags (`--top`, `--no-header`, `--version`) |
| `collections.Counter` | Counts word frequencies |
| `pathlib.Path` | Cross-platform file path handling |
| `sys` | Exit codes and stderr output |

No third-party packages (`pip install ...`) are required to run it.

---

## What Packaging Solves

Without packaging, every user who receives `sample_cli.py` must:

1. Install Python 3.x on their machine.
2. Know how to run `python sample_cli.py ...` from a terminal.
3. Manually manage the correct Python version.

**PyInstaller packaging bundles**:
- The Python interpreter itself (CPython runtime)
- All imported standard-library and third-party modules
- The application code
- Any data files declared in the spec

The result is a single `.exe` (or a folder containing one) that runs on a
compatible Windows machine with **no Python installation required**.

---

## What Packaging Does NOT Solve

| Limitation | Explanation |
|---|---|
| **OS-level runtime libraries** | The exe still requires Windows system DLLs (e.g. `VCRUNTIME140.dll`). If a user has a stripped minimal Windows install, the exe may fail. PyInstaller cannot bundle OS-level DLLs. |
| **Cross-platform portability** | A `.exe` built on Windows runs only on Windows. Building on macOS produces a macOS app bundle. The tool must be re-built on each target OS. |
| **Code confidentiality** | PyInstaller bundles bytecode (`.pyc`), not source, but tools like `uncompyle6` can partially reverse it. PyInstaller is **not** a code obfuscator. |
| **Automatic updates** | A packaged `.exe` does not self-update. An update mechanism (NSIS installer, Squirrel, or manual re-distribution) must be added separately. |
| **Reduced binary size** | The bundled interpreter adds 10–30 MB. PyInstaller does not produce a "small" binary. |

---

## Runtime Architecture After Packaging

When a PyInstaller `--onefile` exe is launched:

1. Windows extracts a temporary directory (`_MEIxxxxxx`) in `%TEMP%`.
2. The Python interpreter and all bundled modules are unpacked there.
3. Your application's `__main__` entry point is executed.
4. On exit, the temporary directory is cleaned up.

For `--onedir` mode (the default), the directory is permanent and placed
next to the exe — useful when startup speed matters or when you want to
inspect bundled files.

---

## Connection to Exercises

`sample_cli.py` is the packaging target used in:
- **11.2** — PyInstaller spec and build script
- **11.3** — Configuration pattern comparison (bad vs. correct)
- **11.4** — Installation procedure
- **11.5** — Release validation checklist

# 11.1 Packaging Concepts

## Core Concept
Python packaging turns a `.py` script into a self-contained executable artifact that users
can run without installing Python. PyInstaller is the standard tool for this on Windows:
it embeds the CPython interpreter, all imported modules, and any data files into a single
`.exe` (one-file mode) or a distributable folder (one-dir mode).

## Key Tools & Concepts
- **PyInstaller** — Bundles Python interpreter + modules + app code into a standalone binary.
- **`--onefile`** — Produces a single `.exe`; self-extracts to `%TEMP%` at runtime. Convenient
  for distribution but slower to launch than one-dir.
- **`--onedir`** (default) — Produces a folder containing the exe and all bundled files.
  Faster startup; easier to inspect and debug.
- **Entry point** — The `if __name__ == "__main__"` block (or a `console_scripts` hook in
  `pyproject.toml`) that PyInstaller uses as the application's start.
- **Hidden imports** — Modules that PyInstaller's static analysis misses (e.g. dynamically
  imported plugins). Must be declared explicitly in the `.spec` file.
- **Data files** — Non-Python assets (JSON configs, images, templates) that the app loads at
  runtime. Must be explicitly listed so PyInstaller copies them into the bundle.

## Why This Matters
Distributing a raw `.py` file requires every recipient to have the right Python version,
the right virtual environment, and some terminal literacy. A packaged exe has none of these
prerequisites — it is a standalone artifact, the same way a compiled C++ program is.

## What Packaging Doesn't Do
It does **not** eliminate OS-level runtime requirements (system DLLs), make code
cross-platform, protect source code from reverse engineering, or provide automatic updates.
See `DEPENDENCY_NOTES.md` for the full breakdown.

## Connection to Exercises
`sample_cli.py` in this folder is the packaging target for the entire skill. It is a real,
testable word-count CLI that exercises `argparse`, `pathlib`, and `collections.Counter` —
all standard-library only, keeping packaging complexity low while still being realistic.
Automated tests for its Python logic live in `tests/test_11_1_packaging_concepts.py`.

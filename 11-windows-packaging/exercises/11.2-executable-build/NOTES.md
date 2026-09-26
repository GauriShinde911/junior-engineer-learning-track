# 11.2 Executable Build with PyInstaller

## Core Concept
PyInstaller converts a Python application into a self-contained Windows executable by
analysing all import chains at build time, copying every required module and binary, and
wrapping them with a CPython interpreter bootloader. The result runs without any Python
installation on the target machine.

## Key Tools & Concepts
- **`build.spec`** — Python-based configuration file that gives PyInstaller full control
  over what gets bundled: source file, hidden imports, data files, output name, icon, and
  one-file vs one-dir mode.
- **`--onefile`** — Packs everything into a single `.exe` that self-extracts to `%TEMP%`
  on each launch. Convenient to distribute; slightly slower to start.
- **`--onedir`** (default in this spec) — Produces a folder containing the exe and all
  bundled modules. Faster startup; preferred for production deployments.
- **`hiddenimports`** — Modules that PyInstaller's static analyser cannot detect (e.g.
  modules loaded via `importlib.import_module()` or `__import__()`). Must be listed
  explicitly or the exe crashes at runtime.
- **`datas`** — Non-Python files (JSON, templates, images) the app reads at runtime.
  Declared as `(source_path, bundle_dest_folder)` pairs.
- **`sys._MEIPASS`** — At runtime inside the exe, PyInstaller sets this attribute to the
  temporary extraction directory. Use `getattr(sys, "_MEIPASS", Path(__file__).parent)`
  to locate bundled data files portably.
- **UPX** — Optional binary compressor that reduces exe size by ~30%. Disable if it causes
  antivirus false-positives.

## Why `build.spec` Over CLI Flags
Using a spec file instead of raw `pyinstaller --onefile sample_cli.py` makes the build
fully reproducible: all configuration is version-controlled, reviewed, and deterministic
across developers and CI pipelines.

## No Automated Tests for This Subsection
The build and run steps are Windows-only, platform-dependent operations. There is no
meaningful pytest test that validates the produced binary in this environment.
See `MANUAL_STEPS.md` for the exact commands to run and verify on a real Windows machine.

## Connection to Exercises
`build.spec` in this folder targets `sample_cli.py` from 11.1. `build.sh` wraps the
PyInstaller invocation as a repeatable script with the Windows PowerShell equivalent
documented inline. `MANUAL_STEPS.md` specifies the exact clean-machine validation procedure.

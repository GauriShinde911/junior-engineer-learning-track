# 1.5 Strings & Files — Quick Reference

## Core Concepts
File handling in Python is managed via stream buffers. To prevent file descriptor leaks, always manage files using context managers (`with` statement). Modern file system operations should utilize object-oriented paths via standard library `pathlib.Path` rather than legacy string concatenations with `os.path`.

## Key Syntax & Patterns
- `with open(path, mode="r", encoding="utf-8") as f:`: Automatically closes file descriptors upon block exit, even if exceptions are raised.
- `path = Path("dir") / "filename.txt"`: Operator overloading `/` builds cross-platform paths seamlessly.
- String transformations: `.split()`, `.strip()`, `.replace()`, and formatted string literals (`f"{val:.2f}"`).

## Standard Library Modules
- `pathlib.Path`: Object-oriented file system paths (`.exists()`, `.read_text()`, `.write_text()`).
- `csv`: Safe parsing and formatting of comma-separated tabular data (`csv.reader`, `csv.writer`).

## Theory to Know
- **Character Encoding**: Python strings are sequences of Unicode characters in memory. Reading from or writing to disk requires encoding/decoding bytes. Always explicitly declare `encoding="utf-8"` to prevent platform-dependent encoding crashes (e.g. Windows `cp1252` vs Linux `utf-8`).
- **Defensive File I/O**: Production code must never assume files exist or are cleanly formatted. Catch `FileNotFoundError` or check `.exists()`, and skip corrupted individual rows without terminating the entire pipeline.

## Connection to What Was Built
- `log_parser.py`: Demonstrates string splitting, custom format validation, and safe line-by-line file consumption.
- `csv_report_generator.py`: Parses CSV records with `csv.reader`, filters malformed rows, and generates structured text reports using `pathlib.Path`.

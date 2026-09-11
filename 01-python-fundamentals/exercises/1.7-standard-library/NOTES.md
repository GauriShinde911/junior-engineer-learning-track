# 1.7 Standard Library — Quick Reference

## Core Concepts
Python's "batteries included" philosophy provides a robust collection of built-in packages that eliminate the need for external third-party dependencies for common tasks like date parsing, serialization, and string pattern matching.

## Standard Library Modules Covered
- `datetime`: High-precision calendar arithmetic, time differences, and string formatting via `datetime.strptime()` and `.strftime()`.
- `pathlib`: Object-oriented filesystem manipulation with cross-platform compatibility.
- `json`: Fast serialization and deserialization between Python dictionaries/lists and JSON text.
- `csv`: Structured delimiter-separated row parsing and output.
- `collections`: Specialized container datatypes, notably `Counter` (multiset frequency tallying) and `defaultdict` (automatic default values for missing keys).
- `re`: Regular expression matching and named group extraction for complex text streams.

## Theory to Know
- **Serialization Trade-offs**: JSON is human-readable, language-agnostic, and safe, but only supports primitive types (strings, numbers, booleans, lists, dicts, null). Complex types like `datetime` or `set` must be converted to primitives prior to serialization.
- **Regular Expressions vs. String Methods**: Prefer fast string methods (`.split()`, `.find()`, `.startswith()`) for simple delimiters; reserve `re` for complex multi-group patterns. Always compile patterns with `re.compile()` if executed in a loop.

## Connection to What Was Built
- `date_calculator.py`: Demonstrates `timedelta` offset math, date differences, and business day calculations.
- `json_transformer.py`: Normalizes and filters JSON schemas with indented output.
- `log_processing_tool.py`: Combines `re` pattern matching, `collections.Counter`, and `datetime` duration analysis into a unified log analytics tool.

# 3.5 Data Validation

Validation is the process of checking that a DataFrame conforms to a defined schema before you process or export it. Good validation returns *actionable* error messages — not just True/False — so the person who owns the data knows exactly what needs fixing.

---

## Core Patterns Used Here

| Pattern | Purpose |
|---|---|
| `pd.api.types.is_numeric_dtype(df[col])` | Check if a column's dtype is numeric |
| `pd.api.types.is_datetime64_any_dtype(df[col])` | Check if a column is parsed as datetime |
| `df[col].isnull()` | Boolean mask — True where value is NaN/None |
| `df[df[col].duplicated(keep=False)]` | Rows that are duplicates of any other row |
| `~df[col].isin(allowed_list)` | Rows whose value is NOT in an allowed set |
| `df.index.tolist()` | Get row indices of flagged rows — needed for error reporting |
| `@dataclass` | Clean container for structured error objects |

---

## Key Ideas

**Schema-driven validation** — define the rules separately from the code. A `Schema` dict specifying required columns, dtypes, ranges, primary key, and allowed values means you can reuse the same `validate()` function for any dataset just by changing the schema.

**Return errors, not exceptions.** Raising an exception on the first failure stops everything. Collecting all errors into a list lets downstream code (or a user) see and fix everything at once — much more useful for data pipelines.

**Primary key checks.** A primary key must be (1) present in every row (no nulls) and (2) unique. Checking both separately gives a clearer error message than a combined check.

**Validate *after* cleaning, not before.** The validator is the final gate before data enters a report or export. Cleaning handles messy input; validation confirms the result meets contract expectations.

---

## What was built here

`excel_validator.py` defines a `Schema` type, a `ValidationError` dataclass, a `ValidationResult` container, and six independent check functions (required columns, dtypes, ranges, primary key, allowed values, null-in-required). The `validate()` function runs all checks and returns a `ValidationResult` with all errors collected. Running it against raw data shows failures; running it against cleaned data shows a pass.

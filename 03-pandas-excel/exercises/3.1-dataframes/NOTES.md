# 3.1 DataFrames

A **DataFrame** is a 2-D labeled table — rows and columns, like a spreadsheet, but in memory. A **Series** is a single column of that table. Together they are the core data structures in pandas.

---

## Core Methods Used Here

| Method / Attribute | Purpose |
|---|---|
| `pd.read_csv(path)` | Load a CSV file into a DataFrame |
| `df.shape` | Tuple `(rows, columns)` |
| `df.dtypes` | Data type inferred for each column |
| `df.head(n)` / `df.tail(n)` | First / last `n` rows |
| `df.describe()` | Min, max, mean, std, percentiles for numeric columns |
| `df["col"]` | Select a single column → returns a Series |
| `df[["col1", "col2"]]` | Select multiple columns → returns a DataFrame |
| `df[df["col"] > x]` | Boolean indexing — filter rows by condition |
| `df["col"].value_counts()` | Frequency count of each unique value |
| `df.isnull().sum()` | Count of null/NaN values per column |
| `df.duplicated()` | Boolean mask — True for duplicate rows |
| `df.select_dtypes(include="number")` | Subset only numeric columns |

---

## Key Ideas

**dtype inference**: When you load a CSV, pandas guesses types — numbers become `int64` or `float64`, everything else becomes `object` (essentially a string column). Mixed-format columns (e.g. `"2024-01-05"` mixed with `"05/01/2024"`) stay as `object` until you explicitly parse them.

**Boolean indexing**: `df[condition]` creates a filtered view — it doesn't modify the original DataFrame. To keep the result, assign it: `filtered = df[df["price"] > 100]`.

**NaN vs null**: pandas uses `float NaN` internally for missing values. `df.isnull()` returns a boolean DataFrame; `.sum()` counts the `True` values per column.

---

## What was built here

`explore_dataset.py` loads `sales_messy.csv` and walks through all major inspection methods step by step — shape, dtypes, head/tail, describe, filtering, value_counts, and null counts.

`data_quality_report.py` is a reusable function (`report()`) that returns a structured dict summarizing nulls, duplicates, numeric stats, and low-cardinality categorical distributions. It's imported by the test suite directly.

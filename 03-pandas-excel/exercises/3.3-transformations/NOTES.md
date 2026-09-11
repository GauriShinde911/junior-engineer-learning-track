# 3.3 Transformations

Transformation converts clean data into shaped, meaningful output — summarized tables, joined datasets, pivots, and derived columns. This is where raw data becomes information.

---

## Core Methods Used Here

| Method | Purpose |
|---|---|
| `df.groupby("col")` | Split data into groups by unique values in a column |
| `.agg({"col": "sum"})` | Apply one or more aggregate functions per group |
| `.agg(alias=("col", "func"))` | Named aggregation — gives the result column a clean name |
| `df["col"].dt.to_period("M")` | Extract year-month period from a datetime column |
| `df.merge(other, on="col", how="left")` | Join two DataFrames on a shared column |
| `pd.pivot_table(df, index=, columns=, values=, aggfunc=)` | Reshape long-format data into a matrix |
| `df["new"] = df["a"] / df["b"]` | Add a calculated column |
| `df.sort_values("col", ascending=False)` | Sort rows by column value |
| `df.drop_duplicates(subset="col", keep="first")` | Keep only first row per unique value in subset |

---

## Key Ideas

**groupby + agg vs pivot_table**: Both group and aggregate, but `pivot_table` reshapes the result into a 2-D matrix (rows = one dimension, columns = another). Use `groupby` when you want a flat summary; use `pivot_table` when you want a cross-tabulation (e.g. product vs month).

**Merge join types**:
- `"left"` — all rows from the left DataFrame; NaN where no match in right.
- `"inner"` — only rows that match in both.
- `"outer"` — all rows from both, NaN where no match.
Left joins are most common for enriching a fact table (sales) with a reference table (products).

**Calculated columns are derived, not stored.** They should always be computed from cleaned source columns, not from other derived columns, to avoid compounding errors.

---

## What was built here

`monthly_summary.py` groups cleaned sales by YYYY-MM period and produces total revenue, order count, average order value, and top product per month.

`cross_table_report.py` joins sales to the products reference table (adding supplier and product_id), adds two calculated columns (revenue_per_unit, est_profit), then builds two pivot tables: product × month and category × region.

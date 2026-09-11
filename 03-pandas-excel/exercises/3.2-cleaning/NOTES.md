# 3.2 Data Cleaning

Cleaning is the process of fixing or removing incorrect, incomplete, inconsistent, or improperly formatted data before analysis. Real-world data almost always needs cleaning — the question is what decisions you make and whether you document them.

---

## Core Methods Used Here

| Method | Purpose |
|---|---|
| `df.drop_duplicates()` | Remove rows that are identical across all (or selected) columns |
| `pd.to_datetime(col, errors="coerce")` | Parse date strings to `datetime64`; unparseable values → NaT |
| `df[col].str.strip()` | Remove leading/trailing whitespace from string values |
| `df[col].str.title()` | Normalize casing — "electronics" → "Electronics" |
| `pd.to_numeric(col, errors="coerce")` | Convert a column to numeric; non-numeric values → NaN |
| `df[col].fillna(value)` | Replace NaN with a specified value |
| `df[col].astype(int)` | Cast column dtype — only safe after all NaNs are filled |
| `df.isnull().sum()` | Count remaining nulls per column — post-cleaning sanity check |
| `df.reset_index(drop=True)` | Re-number the index after dropping rows |

---

## Key Ideas

**Each cleaning step should be a separate function.** This makes steps independently testable and easy to skip or reorder. A monolithic "clean everything" function is harder to debug and extend.

**Document every fill decision.** Filling a null with `0`, `1`, `"Unknown"`, or a column mean are all different business decisions. Leaving them undocumented makes the data silently wrong for anyone who reads it later.

**errors="coerce" is your friend.** Both `pd.to_datetime` and `pd.to_numeric` accept `errors="coerce"` — instead of crashing on bad values, they replace them with NaT/NaN so you can inspect and handle them explicitly.

**Clean before computing derived columns.** Revenue (`qty × unit_price`) was added after qty was fixed and cast — computing it from dirty data would produce incorrect results.

---

## What was built here

`clean_messy_dataset.py` applies 7 documented cleaning steps to `sales_messy.csv`: deduplication, date normalization (3 different input formats), category casing, qty type conversion + null fill, region null fill, sales_rep null fill, and revenue derivation. `ASSUMPTIONS.md` records the rationale for each decision — this is the document you'd share with stakeholders before locking in the cleaning logic.

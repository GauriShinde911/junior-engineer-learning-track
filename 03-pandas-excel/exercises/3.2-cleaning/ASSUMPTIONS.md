# Cleaning Assumptions — sales_messy.csv

This document records every decision made in `clean_messy_dataset.py` and the reasoning behind it.

---

## §1 — Duplicate rows

**Observation**: `ORD-002` appears twice with identical values across all columns.

**Decision**: Drop subsequent duplicates, keep first occurrence.

**Reason**: The row is an exact duplicate — same order_id, same date, same values. It is almost certainly a data-entry or ETL import error. Since both rows are byte-for-byte identical there is no information lost by dropping one.

---

## §2 — Date format normalization

**Observation**: The `date` column contains at least three formats:
- ISO: `2024-01-05`
- US slash: `05/01/2024`
- Natural language: `January 10 2024`
- Dash-separated DMY: `03-02-2024`

**Decision**: Parse all values with `pd.to_datetime(dayfirst=False, infer_datetime_format=True)` and store as a pandas `datetime64` column. Store string representation as `YYYY-MM-DD` on export.

**Reason**: `dayfirst=False` (US convention) is chosen because `05/01/2024` reads as January 5th in the context of the rest of the dataset (which has January dates). If the source was European, `dayfirst=True` would be appropriate — the choice should always be confirmed against business context.

---

## §3 — Category casing

**Observation**: The `category` column has inconsistent casing: `"electronics"`, `"furniture"` (lowercase) alongside `"Electronics"`, `"Furniture"` (title-case).

**Decision**: Apply `.str.title()` to standardize to title-case.

**Reason**: The values are human labels representing the same concept. Inconsistent casing causes groupby to produce separate buckets for the same category. Title-case is the most readable standard form.

---

## §4 — Missing qty values

**Observation**: Two rows have `qty = None/NaN`.

**Decision**: Fill with `1` (minimum plausible order quantity), then cast the entire column from `object` to `int`.

**Reason**: The `qty` column was loaded as `object` because of the mixed presence of string integers and nulls. Dropping these rows would lose valid financial records. A fill value of `1` is conservative — it under-counts rather than inflates revenue. If business rules mandated a different default, this function accepts a parameter.

---

## §5 — Missing region values

**Observation**: One row has `region = NaN`.

**Decision**: Fill with the string `"Unknown"`.

**Reason**: The order has a valid order_id, product, and price. Dropping it would lose revenue data. Labelling it `"Unknown"` makes the gap visible in any downstream groupby or pivot rather than silently excluding the row.

---

## §6 — Missing sales_rep values

**Observation**: One row has `sales_rep = NaN`.

**Decision**: Fill with the string `"Unassigned"`.

**Reason**: Same logic as §5 — the financial record is valid. `"Unassigned"` is a recognizable sentinel value that a downstream report can filter or highlight explicitly.

---

## §7 — Derived `revenue` column

**Decision**: Add `revenue = qty * unit_price` as a final step, after `qty` is cleaned and cast to `int`.

**Reason**: Revenue is a calculated fact, not source data. Computing it in the cleaning pipeline ensures it is always consistent with the cleaned values rather than computed from dirty inputs.

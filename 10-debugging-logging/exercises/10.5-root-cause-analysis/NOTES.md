# 10.5 Root Cause Analysis (RCA) & Regression Prevention

## Core Concepts
Root Cause Analysis (RCA) is the systematic process of discovering the fundamental defect behind an outage or bug rather than merely treating its outward symptoms. Fixing a symptom (e.g. adding a `try/except` that swallows an error or adjusting an arbitrary timeout) leaves the defect latent in the system, guaranteeing future regressions. True RCA isolates the underlying mechanism and guards against recurrence with automated regression tests.

## Symptom vs Root Cause
- **Symptom**: The observable manifestation of failure (e.g. "token expired immediately", "priority 100 ran last", "ledger off by 2 cents").
- **Root Cause**: The foundational flaw that triggered the chain of events (e.g. "comparing timezone-naive local clock with UTC", "lexicographical string sorting", "IEEE-754 binary float addition drift").
- **The "5 Whys" Method**: Iteratively asks "Why did this happen?" until reaching an architectural, procedural, or boundary condition flaw rather than stopping at the first proximate error.

## Key Techniques & Tools
- **Minimal Reproducible Example (MRE)**: Reducing a complex multi-service failure to a 5-line standalone Python script that reliably triggers the defect.
- `decimal.Decimal`: Provides exact fixed-point decimal arithmetic for financial systems to eliminate floating point imprecision.
- `copy.deepcopy()`: Creates independent recursive copies of compound objects to eliminate shared mutable state.
- Non-greedy regex (`.*?`): Constrains pattern matching to the minimal necessary span.

## Connection to Exercises
In `defect_1.py` through `defect_5.py`, we analyzed 5 realistic production defects (timezone disparity, string sorting, shallow copying, float drift, greedy regex matching). In `RCA_REPORTS.md`, we documented complete root-cause incident analyses, minimal reproductions, and regression test suites.

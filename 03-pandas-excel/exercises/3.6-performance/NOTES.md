# 3.6 Performance

pandas performance is about avoiding Python-level loops. The library is built on NumPy, which stores data as contiguous C arrays and performs operations in compiled code. Any time you loop row-by-row in Python you throw that away.

---

## Core Methods & Patterns Used Here

| Method / Pattern | Purpose |
|---|---|
| `np.select(conditions, choices, default)` | Apply if/elif/else logic across an entire array — no Python loop |
| `df[col].where(condition, other)` | Replace values where condition is False — vectorized conditional |
| `df[col] * scalar` | Element-wise arithmetic — all rows at once |
| `time.perf_counter()` | High-resolution timer for benchmarking |
| `np.random.default_rng(seed)` | Reproducible random data generation |
| `df.apply(fn, axis=1)` | Row-by-row apply — slower than np.select but cleaner than a for-loop for complex logic |

---

## Key Ideas

**Why vectorization wins:** A Python `for i in range(len(df))` loop runs every row through the CPython interpreter — type checks, GC bookkeeping, function dispatch. NumPy/pandas vectorized functions are implemented in C and operate on contiguous memory arrays in a single compiled pass. On 100k rows the speedup is typically **50–200×**. At 1M rows, it's even wider.

**`np.select` is the vectorized if/elif/else.** It takes a list of conditions (boolean arrays) and a list of corresponding values, evaluated in order, and returns an array — exactly like a chain of `if/elif/else` but across every row simultaneously.

**When is `.apply()` acceptable?** `.apply(fn, axis=1)` is cleaner than a for-loop but still calls `fn` once per row in Python. Use it only when no vectorized alternative exists (e.g. calling an external API or a highly irregular transformation). For any arithmetic or conditional logic, `np.select` / `.where()` / Series arithmetic will always be faster.

**Chunking (concept):** For datasets too large to fit in RAM, `pd.read_csv(path, chunksize=N)` returns an iterator of DataFrames. Process each chunk and accumulate results. This keeps memory flat at `N rows × dtype overhead` regardless of file size.

---

## What was built here

`slow_vs_vectorized.py` generates a 100,000-row dataset, then applies a tiered discount (4 tiers based on qty) two ways: a Python for-loop using `df.iloc[i]` and a vectorized version using `np.select`. Both produce identical results. The script prints the execution time for each and the speedup ratio, then explains in plain language why the gap exists.

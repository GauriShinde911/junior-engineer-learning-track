"""
3.6 Performance — slow_vs_vectorized.py

Implements the SAME transformation two ways on a 100,000-row generated
dataset, then prints a side-by-side timing comparison:

  Transformation: apply a tiered discount based on qty
    - qty >= 50  → 15% discount
    - qty >= 20  → 10% discount
    - qty >= 10  →  5% discount
    - else       →  0% discount
  Then: discounted_price = unit_price * (1 - discount_rate)

WHY VECTORIZATION WINS
──────────────────────
A Python for-loop runs one row at a time through the CPython interpreter,
which is slow because every iteration incurs Python overhead: type checking,
garbage-collector bookkeeping, and function call dispatch. pandas vectorized
operations (including np.select, .where(), .apply() on the whole Series, and
arithmetic on Series objects) are implemented in C and operate on contiguous
NumPy arrays in memory. They process all rows in a single compiled pass,
with no Python-level loop per row. On a 100k-row dataset the difference is
typically 50–200x. The larger the dataset, the bigger the gap.

Run:
    python 03-pandas-excel/exercises/3.6-performance/slow_vs_vectorized.py
"""

import time
import pandas as pd
import numpy as np

N_ROWS = 100_000
RANDOM_SEED = 42


def generate_dataset(n: int = N_ROWS) -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)
    products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Headphones", "Webcam"]
    return pd.DataFrame({
        "order_id": [f"ORD-{i:07d}" for i in range(n)],
        "product": rng.choice(products, n),
        "qty": rng.integers(1, 101, n),
        "unit_price": rng.uniform(100, 80_000, n).round(2),
    })


# ── VERSION 1: Python for-loop (slow) ────────────────────────────────

def apply_discount_loop(df: pd.DataFrame) -> pd.Series:
    """
    Row-by-row Python for-loop.
    Each iteration goes through the CPython interpreter —
    no C-level batching.
    """
    results = []
    for i in range(len(df)):
        qty = df.iloc[i]["qty"]
        price = df.iloc[i]["unit_price"]
        if qty >= 50:
            rate = 0.15
        elif qty >= 20:
            rate = 0.10
        elif qty >= 10:
            rate = 0.05
        else:
            rate = 0.0
        results.append(round(price * (1 - rate), 2))
    return pd.Series(results, index=df.index)


# ── VERSION 2: Vectorized with np.select (fast) ───────────────────────

def apply_discount_vectorized(df: pd.DataFrame) -> pd.Series:
    """
    np.select evaluates conditions on entire NumPy arrays in C.
    No Python-level loop — all rows processed in a single pass.
    """
    conditions = [
        df["qty"] >= 50,
        df["qty"] >= 20,
        df["qty"] >= 10,
    ]
    rates = [0.15, 0.10, 0.05]
    discount_rate = np.select(conditions, rates, default=0.0)
    return (df["unit_price"] * (1 - discount_rate)).round(2)


# ── Timing harness ────────────────────────────────────────────────────

def time_run(fn, df: pd.DataFrame, label: str) -> tuple[pd.Series, float]:
    start = time.perf_counter()
    result = fn(df)
    elapsed = time.perf_counter() - start
    print(f"  {label:<35} {elapsed:.4f} s")
    return result, elapsed


def verify_equal(a: pd.Series, b: pd.Series) -> bool:
    """Confirm both implementations produce identical output."""
    return a.equals(b)


if __name__ == "__main__":
    print(f"\nGenerating {N_ROWS:,}-row dataset …")
    df = generate_dataset()
    print(f"Dataset shape: {df.shape}")

    print("\nRunning timing comparison (both apply the same tiered discount):")
    print("-" * 55)

    # Warm up (avoid cold-start noise)
    _ = apply_discount_vectorized(df.head(1000))

    result_loop, t_loop = time_run(apply_discount_loop, df, "Python for-loop")
    result_vec,  t_vec  = time_run(apply_discount_vectorized, df, "Vectorized (np.select)")

    print("-" * 55)
    if t_vec > 0:
        speedup = t_loop / t_vec
        print(f"\n  Speedup: {speedup:.1f}× faster (vectorized vs loop)")

    # Verify correctness
    equal = verify_equal(result_loop, result_vec)
    print(f"  Results identical: {equal}")

    print()
    print("  Sample output (first 5 rows):")
    sample = df.head(5).copy()
    sample["discounted_price_loop"] = result_loop.head(5)
    sample["discounted_price_vec"]  = result_vec.head(5)
    print(sample[["order_id", "qty", "unit_price",
                  "discounted_price_loop", "discounted_price_vec"]].to_string(index=False))

    print("""
WHY VECTORIZATION WINS
──────────────────────
A Python for-loop runs one row at a time through the CPython interpreter —
every iteration incurs type-checking, GC bookkeeping, and dispatch overhead.
Vectorized operations (np.select, Series arithmetic) are implemented in C
and operate on contiguous NumPy arrays. They process all rows in a single
compiled pass with zero Python-level iteration.

On 100k rows the gap is 50–200×. At 1M rows it's even wider.
Rule of thumb: if you find yourself writing `for i in range(len(df)):`
in a pandas workflow, there is almost always a vectorized equivalent.
""")

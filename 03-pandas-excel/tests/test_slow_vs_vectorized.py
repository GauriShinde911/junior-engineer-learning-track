"""Unit tests for 3.6 slow_vs_vectorized."""

import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "3.6-performance"

sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))

from slow_vs_vectorized import generate_dataset, apply_discount_loop, apply_discount_vectorized, verify_equal


def test_vectorized_matches_loop():
    df = generate_dataset(100)
    res_loop = apply_discount_loop(df)
    res_vec = apply_discount_vectorized(df)
    assert verify_equal(res_loop, res_vec)

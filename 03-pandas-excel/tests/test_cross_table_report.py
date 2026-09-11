"""Unit tests for 3.3 cross_table_report."""

import sys
from pathlib import Path
import pandas as pd

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "3.3-transformations"
CLEANING_DIR = MODULE_DIR / "exercises" / "3.2-cleaning"
sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))
sys.path.insert(0, str(CLEANING_DIR))

from cross_table_report import (
    load_products,
    build_enriched,
    add_calculated_columns,
    build_pivot,
    build_category_region_pivot,
)
from clean_messy_dataset import clean, RAW_FILE


def test_cross_table_components():
    sales_df = clean(RAW_FILE)
    products_df = load_products()
    enriched = build_enriched(sales_df, products_df)
    for col in ["supplier", "product_id", "reorder_level"]:
        assert col in enriched.columns
    enriched_calc = add_calculated_columns(enriched)
    assert "revenue_per_unit" in enriched_calc.columns
    assert "margin_pct" in enriched_calc.columns

    prod_pivot = build_pivot(enriched_calc)
    assert "TOTAL" in prod_pivot.columns
    assert not prod_pivot.empty

    cat_region = build_category_region_pivot(enriched_calc)
    assert "TOTAL" in cat_region.columns
    assert not cat_region.empty

"""Unit tests for 3.5 excel_validator."""

import sys
from pathlib import Path
import pandas as pd

TEST_DIR = Path(__file__).resolve().parent
MODULE_DIR = TEST_DIR.parent
SUBSECTION_DIR = MODULE_DIR / "exercises" / "3.5-validation"
CLEANING_DIR = MODULE_DIR / "exercises" / "3.2-cleaning"

sys.path.insert(0, str(MODULE_DIR))
sys.path.insert(0, str(SUBSECTION_DIR))
sys.path.insert(0, str(CLEANING_DIR))

from excel_validator import validate, SALES_SCHEMA
from clean_messy_dataset import clean, RAW_FILE


def test_validator_on_clean_data():
    clean_df = clean(RAW_FILE)
    result = validate(clean_df, SALES_SCHEMA)
    assert result.passed is True
    assert len(result.errors) == 0


def test_validator_on_raw_data():
    raw_df = pd.read_csv(RAW_FILE)
    result = validate(raw_df, SALES_SCHEMA)
    assert result.passed is False
    assert len(result.errors) > 0

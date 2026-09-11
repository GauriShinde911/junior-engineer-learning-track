"""
3.5 Validation — excel_validator.py

A reusable validator that checks a DataFrame against a schema.
Returns actionable error messages — not just True/False.

Schema definition:
  {
    "required_columns": [...],
    "dtypes": {"col": "numeric" | "string" | "datetime"},
    "ranges": {"col": (min, max)},
    "primary_key": "col_name"  # must be unique, no nulls
    "allowed_values": {"col": [...]}
  }

Run:
    python 03-pandas-excel/exercises/3.5-validation/excel_validator.py
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
import pandas as pd
import sys

SKILL_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SKILL_ROOT / "03-pandas-excel" / "exercises" / "3.2-cleaning"))
from clean_messy_dataset import clean, RAW_FILE


# ── Error container ───────────────────────────────────────────────────

@dataclass
class ValidationError:
    column: str
    rule: str
    message: str
    affected_rows: list[int] = field(default_factory=list)

    def __str__(self) -> str:
        rows_str = f" (rows: {self.affected_rows})" if self.affected_rows else ""
        return f"[{self.rule}] {self.column}: {self.message}{rows_str}"


@dataclass
class ValidationResult:
    passed: bool
    errors: list[ValidationError] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return "✓ Validation PASSED — no errors found."
        lines = [f"✗ Validation FAILED — {len(self.errors)} error(s) found:"]
        for err in self.errors:
            lines.append(f"  • {err}")
        return "\n".join(lines)


# ── Schema type ───────────────────────────────────────────────────────

Schema = dict[str, Any]

SALES_SCHEMA: Schema = {
    "required_columns": ["order_id", "date", "product", "category", "qty",
                         "unit_price", "region", "sales_rep", "revenue"],
    "dtypes": {
        "qty": "numeric",
        "unit_price": "numeric",
        "revenue": "numeric",
        "date": "datetime",
    },
    "ranges": {
        "qty": (1, 1000),
        "unit_price": (1, 500_000),
        "revenue": (1, 50_000_000),
    },
    "primary_key": "order_id",
    "allowed_values": {
        "category": ["Electronics", "Accessories", "Furniture"],
        "region": ["North", "South", "East", "West", "Unknown"],
    },
}


# ── Individual validation checks ──────────────────────────────────────

def check_required_columns(df: pd.DataFrame, schema: Schema) -> list[ValidationError]:
    errors: list[ValidationError] = []
    required = schema.get("required_columns", [])
    missing = [c for c in required if c not in df.columns]
    if missing:
        errors.append(ValidationError(
            column=", ".join(missing),
            rule="required_columns",
            message=f"Column(s) missing from DataFrame: {missing}"
        ))
    return errors


def check_dtypes(df: pd.DataFrame, schema: Schema) -> list[ValidationError]:
    errors: list[ValidationError] = []
    dtype_rules = schema.get("dtypes", {})
    for col, expected_kind in dtype_rules.items():
        if col not in df.columns:
            continue
        if expected_kind == "numeric":
            if not pd.api.types.is_numeric_dtype(df[col]):
                null_count = df[col].isnull().sum()
                errors.append(ValidationError(
                    column=col,
                    rule="dtype",
                    message=f"Expected numeric dtype, got '{df[col].dtype}'. "
                            f"{null_count} null(s) present."
                ))
        elif expected_kind == "datetime":
            if not pd.api.types.is_datetime64_any_dtype(df[col]):
                errors.append(ValidationError(
                    column=col,
                    rule="dtype",
                    message=f"Expected datetime dtype, got '{df[col].dtype}'."
                ))
        elif expected_kind == "string":
            if df[col].dtype not in ("object", "string"):
                errors.append(ValidationError(
                    column=col,
                    rule="dtype",
                    message=f"Expected string/object dtype, got '{df[col].dtype}'."
                ))
    return errors


def check_ranges(df: pd.DataFrame, schema: Schema) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for col, (lo, hi) in schema.get("ranges", {}).items():
        if col not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue
        out_of_range = df[(df[col] < lo) | (df[col] > hi)]
        if not out_of_range.empty:
            errors.append(ValidationError(
                column=col,
                rule="range",
                message=f"Values outside [{lo}, {hi}]. Found {len(out_of_range)} row(s).",
                affected_rows=out_of_range.index.tolist()
            ))
    return errors


def check_primary_key(df: pd.DataFrame, schema: Schema) -> list[ValidationError]:
    errors: list[ValidationError] = []
    pk_col = schema.get("primary_key")
    if not pk_col or pk_col not in df.columns:
        return errors

    # Check nulls
    null_rows = df[df[pk_col].isnull()]
    if not null_rows.empty:
        errors.append(ValidationError(
            column=pk_col,
            rule="primary_key_null",
            message=f"Primary key contains {len(null_rows)} null value(s).",
            affected_rows=null_rows.index.tolist()
        ))

    # Check duplicates
    dup_rows = df[df[pk_col].duplicated(keep=False)]
    if not dup_rows.empty:
        dup_vals = dup_rows[pk_col].unique().tolist()
        errors.append(ValidationError(
            column=pk_col,
            rule="primary_key_duplicate",
            message=f"Primary key has {len(dup_rows)} duplicate row(s). "
                    f"Duplicate values: {dup_vals}",
            affected_rows=dup_rows.index.tolist()
        ))
    return errors


def check_allowed_values(df: pd.DataFrame, schema: Schema) -> list[ValidationError]:
    errors: list[ValidationError] = []
    for col, allowed in schema.get("allowed_values", {}).items():
        if col not in df.columns:
            continue
        bad_rows = df[~df[col].isin(allowed) & df[col].notna()]
        if not bad_rows.empty:
            bad_vals = bad_rows[col].unique().tolist()
            errors.append(ValidationError(
                column=col,
                rule="allowed_values",
                message=f"Unexpected value(s): {bad_vals}. Allowed: {allowed}",
                affected_rows=bad_rows.index.tolist()
            ))
    return errors


def check_nulls_in_required(df: pd.DataFrame, schema: Schema) -> list[ValidationError]:
    """Flag nulls in required columns that are present."""
    errors: list[ValidationError] = []
    for col in schema.get("required_columns", []):
        if col not in df.columns:
            continue
        null_rows = df[df[col].isnull()]
        if not null_rows.empty:
            errors.append(ValidationError(
                column=col,
                rule="null_in_required",
                message=f"{len(null_rows)} null value(s) in required column.",
                affected_rows=null_rows.index.tolist()
            ))
    return errors


# ── Main validator ────────────────────────────────────────────────────

def validate(df: pd.DataFrame, schema: Schema) -> ValidationResult:
    """
    Run all validation checks and return a ValidationResult.
    Checks run in order: required_columns first (other checks are skipped
    for columns that don't exist).
    """
    errors: list[ValidationError] = []

    errors.extend(check_required_columns(df, schema))
    errors.extend(check_dtypes(df, schema))
    errors.extend(check_ranges(df, schema))
    errors.extend(check_primary_key(df, schema))
    errors.extend(check_allowed_values(df, schema))
    errors.extend(check_nulls_in_required(df, schema))

    return ValidationResult(passed=len(errors) == 0, errors=errors)


if __name__ == "__main__":
    print("\n── Running against CLEAN data (should PASS) ──")
    clean_df = clean(RAW_FILE)
    result = validate(clean_df, SALES_SCHEMA)
    print(result.summary())

    print("\n── Running against RAW data (should FAIL) ──")
    raw_df = pd.read_csv(RAW_FILE)
    result_raw = validate(raw_df, SALES_SCHEMA)
    print(result_raw.summary())

"""
Tests for 1.7 Standard Library
Covers: date_calculator, json_transformer, log_processing_tool.
"""

from datetime import date
import json
import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.7-standard-library"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from date_calculator import (
    add_business_days,
    add_days,
    days_between,
    get_relative_time_description
)
from json_transformer import transform_records
from log_processing_tool import (
    analyze_log_file,
    export_analysis_to_json,
    parse_structured_log_line
)


# =====================================================================
# Date Calculator Tests
# =====================================================================
def test_date_calculator_differences_and_offsets():
    assert days_between("2026-01-01", "2026-01-10") == 9
    assert add_days("2026-01-01", 10) == "2026-01-11"

    # Friday 2026-01-02 + 1 business day should be Monday 2026-01-05
    assert add_business_days("2026-01-02", 1) == "2026-01-05"


def test_relative_time_descriptions():
    today = date(2026, 1, 10)
    assert get_relative_time_description("2026-01-10", reference_date=today) == "today"
    assert get_relative_time_description("2026-01-11", reference_date=today) == "tomorrow"
    assert get_relative_time_description("2026-01-09", reference_date=today) == "yesterday"
    assert get_relative_time_description("2026-01-15", reference_date=today) == "in 5 days"
    assert get_relative_time_description("2026-01-05", reference_date=today) == "5 days ago"


# =====================================================================
# JSON Transformer Tests
# =====================================================================
def test_json_transformer(tmp_path):
    in_file = tmp_path / "people.json"
    out_file = tmp_path / "adults.json"

    data = [
        {"name": "Alice", "age": 25, "city": "chicago"},
        {"name": "Kid", "age": 12, "city": "chicago"},
        {"name": "Bob", "age": 40, "city": "boston"}
    ]
    in_file.write_text(json.dumps(data), encoding="utf-8")

    transformed = transform_records(in_file, out_file, min_age=18)
    assert len(transformed) == 2
    # Sorted age desc: Bob (40) first, Alice (25) second
    assert transformed[0]["full_name"] == "Bob"
    assert transformed[0]["city"] == "Boston"
    assert out_file.exists()


def test_json_transformer_missing_file():
    with pytest.raises(FileNotFoundError):
        transform_records("missing_file_abc.json", "out.json")


def test_json_transformer_invalid_json(tmp_path):
    bad_file = tmp_path / "corrupt.json"
    bad_file.write_text("{not a valid json}", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid JSON"):
        transform_records(bad_file, tmp_path / "out.json")


# =====================================================================
# Log Processing Tool Tests (Regex + Collections)
# =====================================================================
def test_parse_structured_log_line():
    valid_line = "[2026-01-10 14:00:00] ERROR - [payment] Gateway timeout"
    parsed = parse_structured_log_line(valid_line)
    assert parsed is not None
    assert parsed["level"] == "ERROR"
    assert parsed["module"] == "payment"
    assert parsed["message"] == "Gateway timeout"

    assert parse_structured_log_line("INVALID LOG FORMAT") is None


def test_analyze_log_file(tmp_path):
    log_file = tmp_path / "test.log"
    out_json = tmp_path / "metrics.json"

    log_file.write_text(
        "[2026-01-10 10:00:00] INFO - [auth] Login\n"
        "[2026-01-10 10:05:00] ERROR - [auth] Bad password\n"
        "SKIP ME PLEASE\n"
        "[2026-01-10 10:10:00] INFO - [db] Query ok\n",
        encoding="utf-8"
    )

    report = analyze_log_file(log_file)
    assert report["valid_log_entries"] == 3
    assert report["corrupt_lines"] == 1
    assert report["level_counts"]["INFO"] == 2
    assert report["level_counts"]["ERROR"] == 1
    assert report["time_span"]["duration_seconds"] == 600.0

    export_analysis_to_json(report, out_json)
    assert out_json.exists()


def test_analyze_log_file_missing():
    with pytest.raises(FileNotFoundError):
        analyze_log_file("missing_log_999.log")

"""
Tests for 1.5 Strings & Files
Covers: log_parser, csv_report_generator (pathlib, safe file reading, error tolerance).
"""

import sys
from pathlib import Path
import pytest

MODULE_ROOT = Path(__file__).resolve().parent.parent
SUBSECTION_DIR = MODULE_ROOT / "exercises" / "1.5-strings-files"
if str(SUBSECTION_DIR) not in sys.path:
    sys.path.insert(0, str(SUBSECTION_DIR))

from log_parser import (
    InvalidLogFormat,
    parse_log_file,
    parse_log_line,
    summarize_log_levels
)
from csv_report_generator import generate_sales_report


# =====================================================================
# Log Parser Tests
# =====================================================================
def test_parse_log_line_valid():
    entry = parse_log_line("2026-01-01 12:00:00 | INFO | System started")
    assert entry["timestamp"] == "2026-01-01 12:00:00"
    assert entry["level"] == "INFO"
    assert entry["message"] == "System started"


def test_parse_log_line_invalid():
    with pytest.raises(InvalidLogFormat):
        parse_log_line("Not a valid delimiter line")

    with pytest.raises(InvalidLogFormat):
        parse_log_line("   ")


def test_parse_log_file_with_bad_lines(tmp_path):
    log_file = tmp_path / "app.log"
    log_file.write_text(
        "2026-01-01 00:00:01 | INFO | Booting\n"
        "MALFORMED_LINE\n"
        "2026-01-01 00:00:02 | ERROR | Out of memory\n",
        encoding="utf-8"
    )

    entries, skipped = parse_log_file(log_file)
    assert len(entries) == 2
    assert skipped == 1
    assert summarize_log_levels(entries) == {"INFO": 1, "ERROR": 1}


def test_parse_log_file_missing_does_not_crash():
    entries, skipped = parse_log_file("missing_non_existent_file.log")
    assert entries == []
    assert skipped == 0


# =====================================================================
# CSV Report Generator Tests
# =====================================================================
def test_generate_sales_report(tmp_path):
    csv_file = tmp_path / "sales.csv"
    report_file = tmp_path / "out" / "sales_report.txt"

    csv_file.write_text(
        "Product,Quantity,Price\n"
        "Mouse,10,20.0\n"
        "Corrupted,not_a_num,30\n"
        "Keyboard,5,80.0\n",
        encoding="utf-8"
    )

    summary = generate_sales_report(csv_file, report_file)
    assert summary is not None
    assert summary["valid_rows"] == 2
    assert summary["skipped_rows"] == 1
    assert summary["total_revenue"] == 600.0
    assert summary["best_seller"] == "Mouse"
    assert report_file.exists()


def test_generate_sales_report_missing_file_does_not_crash():
    res = generate_sales_report("non_existent_sales.csv", "out.txt")
    assert res is None

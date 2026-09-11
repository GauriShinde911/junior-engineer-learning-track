"""
1.7 Standard Library: Advanced Log Processing Tool
Demonstrates: re (regular expressions), collections.Counter, collections.defaultdict,
datetime parsing, pathlib.Path, and json export using ONLY the standard library.
"""

from collections import Counter, defaultdict
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Union

# Regex pattern matching: [2026-01-10 14:23:45] LEVEL - [module] message
LOG_PATTERN = re.compile(
    r"^\[(?P<timestamp>\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})\]\s+"
    r"(?P<level>[A-Z]+)\s+-\s+"
    r"(\[(?P<module>[^\]]+)\]\s+)?(?P<message>.*)$"
)


def parse_structured_log_line(line: str) -> Optional[Dict[str, Any]]:
    """Extracts regex groups from a formatted log line."""
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    data = match.groupdict()
    return {
        "timestamp": datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S"),
        "level": data["level"].upper(),
        "module": data.get("module") or "root",
        "message": data["message"].strip()
    }


def analyze_log_file(filepath: Union[str, Path]) -> Dict[str, Any]:
    """
    Scans a log file, aggregates error frequencies using Counter,
    groups messages by module using defaultdict, and determines time span.
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    level_counter: Counter = Counter()
    module_counter: Counter = Counter()
    timestamps: List[datetime] = []
    total_lines = 0
    matched_lines = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            total_lines += 1
            entry = parse_structured_log_line(line)
            if entry:
                matched_lines += 1
                level_counter[entry["level"]] += 1
                module_counter[entry["module"]] += 1
                timestamps.append(entry["timestamp"])

    timestamps.sort()
    time_span = None
    if timestamps:
        duration_seconds = (timestamps[-1] - timestamps[0]).total_seconds()
        time_span = {
            "start": timestamps[0].strftime("%Y-%m-%d %H:%M:%S"),
            "end": timestamps[-1].strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration_seconds
        }

    return {
        "total_lines_read": total_lines,
        "valid_log_entries": matched_lines,
        "corrupt_lines": total_lines - matched_lines,
        "level_counts": dict(level_counter),
        "module_activity": dict(module_counter.most_common(5)),
        "time_span": time_span
    }


def export_analysis_to_json(analysis_results: Dict[str, Any], output_path: Union[str, Path]) -> None:
    """Exports the analysis dictionary to JSON with indentation."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2)


if __name__ == "__main__":
    demo_log = Path("system_activity.log")
    demo_report = Path("log_metrics.json")

    sample_logs = (
        "[2026-01-10 12:00:00] INFO - [auth] User login successful for alice\n"
        "[2026-01-10 12:05:12] WARNING - [db] Slow query took 1250ms\n"
        "GARBAGE TEXT LINE TO TEST RESILIENCE\n"
        "[2026-01-10 12:15:30] ERROR - [payment] Card declined: insufficient funds\n"
        "[2026-01-10 12:30:45] INFO - [auth] User logout for alice\n"
    )
    demo_log.write_text(sample_logs, encoding="utf-8")

    report = analyze_log_file(demo_log)
    export_analysis_to_json(report, demo_report)

    print("Log Analysis Completed:")
    print("Level Distribution:", report["level_counts"])
    print("Module Distribution:", report["module_activity"])
    print("Saved Metrics JSON:", demo_report.name)

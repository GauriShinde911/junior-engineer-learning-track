"""
1.5 Strings & Files: Robust Log Parser
Demonstrates: String parsing, pathlib.Path, safe file reading with context managers,
explicit utf-8 encoding, and non-crashing handling of missing/corrupt files.
"""

from pathlib import Path
from typing import Dict, List, Tuple, Union


class InvalidLogFormat(Exception):
    """Raised when a log line fails to match the expected format."""
    pass


def parse_log_line(line: str) -> Dict[str, str]:
    """
    Parses a single log line formatted as:
    TIMESTAMP | LEVEL | MESSAGE
    """
    stripped = line.strip()
    if not stripped:
        raise InvalidLogFormat("Encountered empty line.")

    parts = stripped.split(" | ")
    if len(parts) != 3:
        raise InvalidLogFormat(f"Expected 3 parts separated by ' | ', got {len(parts)}: '{stripped}'")

    timestamp, level, message = parts
    level_cleaned = level.strip().upper()

    if not timestamp.strip() or not level_cleaned or not message.strip():
        raise InvalidLogFormat(f"Log entry has blank fields: '{stripped}'")

    return {
        "timestamp": timestamp.strip(),
        "level": level_cleaned,
        "message": message.strip()
    }


def parse_log_file(filepath: Union[str, Path]) -> Tuple[List[Dict[str, str]], int]:
    """
    Safely reads and parses a log file line by line using pathlib.
    Does NOT crash on missing file; returns empty list and logs error.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"[Warning] Log file does not exist: {path}")
        return [], 0

    valid_entries: List[Dict[str, str]] = []
    skipped_count = 0

    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                try:
                    entry = parse_log_line(line)
                    valid_entries.append(entry)
                except InvalidLogFormat as err:
                    skipped_count += 1
                    # Graceful non-crashing skip
    except (IOError, OSError) as err:
        print(f"[Error] Failed to read {path}: {err}")
        return [], 0

    return valid_entries, skipped_count


def summarize_log_levels(entries: List[Dict[str, str]]) -> Dict[str, int]:
    """Tallies count of entries per log severity level."""
    counts: Dict[str, int] = {}
    for entry in entries:
        lvl = entry["level"]
        counts[lvl] = counts.get(lvl, 0) + 1
    return counts


if __name__ == "__main__":
    demo_file = Path("sample.log")

    # Generate sample file if it doesn't exist
    if not demo_file.exists():
        sample_content = (
            "2026-01-10 10:00:01 | INFO | Application initialized\n"
            "CORRUPTED LINE WITHOUT DELIMITER\n"
            "2026-01-10 10:05:22 | WARNING | High memory consumption detected\n"
            "2026-01-10 10:15:30 | ERROR | Connection timed out to DB\n"
            "\n"
            "2026-01-10 10:20:00 | INFO | Request served in 42ms\n"
        )
        demo_file.write_text(sample_content, encoding="utf-8")

    entries, skipped = parse_log_file(demo_file)
    print(f"Parsed {len(entries)} valid log lines, skipped {skipped} malformed lines.")
    print("Severity Summary:", summarize_log_levels(entries))

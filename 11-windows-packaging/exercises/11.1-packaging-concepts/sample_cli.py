"""
sample_cli.py - Word Count & File Summary CLI

A small but real command-line utility used as the packaging target
throughout exercises 11.1–11.4. It accepts a text file as input and
reports character count, word count, line count, and optionally the
top-N most frequent words.

Usage:
    python sample_cli.py <filepath> [--top N] [--no-header]

Examples:
    python sample_cli.py report.txt
    python sample_cli.py report.txt --top 5
    python sample_cli.py report.txt --top 10 --no-header
"""

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


APP_VERSION = "1.0.0"
APP_NAME = "wc-summary"


def count_text(content: str) -> Dict[str, int]:
    """Return character, word, and line counts for the given text."""
    return {
        "chars": len(content),
        "words": len(content.split()),
        "lines": content.count("\n") + (1 if content and not content.endswith("\n") else 0),
    }


def top_words(content: str, n: int) -> List[Tuple[str, int]]:
    """Return the top-N most frequent words (case-insensitive, alpha only)."""
    words = [w.strip(".,!?;:\"'()[]") for w in content.lower().split()]
    words = [w for w in words if w.isalpha()]
    counter = Counter(words)
    return counter.most_common(n)


def format_report(
    filepath: str,
    counts: Dict[str, int],
    top: Optional[List[Tuple[str, int]]],
    show_header: bool,
) -> str:
    lines = []
    if show_header:
        lines.append(f"{APP_NAME} v{APP_VERSION}  —  {filepath}")
        lines.append("-" * 50)
    lines.append(f"  Characters : {counts['chars']:>10,}")
    lines.append(f"  Words      : {counts['words']:>10,}")
    lines.append(f"  Lines      : {counts['lines']:>10,}")
    if top:
        lines.append("")
        lines.append(f"  Top {len(top)} words:")
        for rank, (word, freq) in enumerate(top, start=1):
            lines.append(f"    {rank:>3}. {word:<20} {freq:>6}")
    return "\n".join(lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Count characters, words, and lines in a text file.",
    )
    parser.add_argument("filepath", help="Path to the text file to analyse")
    parser.add_argument(
        "--top",
        type=int,
        default=0,
        metavar="N",
        help="Show top N most frequent words (default: 0 = disabled)",
    )
    parser.add_argument(
        "--no-header",
        dest="no_header",
        action="store_true",
        help="Suppress the header/title line",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    return parser.parse_args(argv)


def run(argv: Optional[List[str]] = None) -> int:
    """Main entry point. Returns exit code."""
    args = parse_args(argv)
    path = Path(args.filepath)

    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1
    if not path.is_file():
        print(f"Error: path is not a file: {path}", file=sys.stderr)
        return 1

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 1

    counts = count_text(content)
    frequent = top_words(content, args.top) if args.top > 0 else None
    report = format_report(
        filepath=str(path),
        counts=counts,
        top=frequent,
        show_header=not args.no_header,
    )
    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(run())

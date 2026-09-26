"""
app_with_bad_config.py - Configuration Hardcoded Inside the Bundle

Demonstrates the WRONG pattern: configuration values are baked into the
Python source that gets bundled by PyInstaller.

Problems with this approach:
1. To change any setting (e.g. output directory, log level, max results),
   a developer must edit the source file and re-run pyinstaller.
2. The config cannot be changed by IT administrators or end-users without
   access to the source repository.
3. Different deployment environments (dev / staging / production) require
   separate builds from separate source branches, making releases error-prone.
4. Secrets (API keys, passwords) accidentally baked in here are extractable
   from the .pyc bytecode inside the bundle.
"""

import sys
from pathlib import Path
from collections import Counter

# ── HARDCODED CONFIGURATION (wrong pattern) ──────────────────────────────────
OUTPUT_DIR = "C:\\Users\\admin\\wc_output"          # Breaks on every other user account
MAX_RESULTS = 10                                    # Immutable without a rebuild
LOG_LEVEL = "INFO"                                  # Cannot be tuned by ops without rebuild
APP_TITLE = "Word Count Summary — Production v1"   # Baked-in string, not updateable


def run_bad_config(filepath: str) -> None:
    """
    Runs the word-count tool using the hardcoded configuration above.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    words = [w.strip(".,!?;:\"'()[]").lower() for w in content.split() if w.isalpha()]
    top = Counter(words).most_common(MAX_RESULTS)

    print(APP_TITLE)
    print(f"Config: output_dir={OUTPUT_DIR}, max_results={MAX_RESULTS}, log_level={LOG_LEVEL}")
    print(f"File  : {path}")
    print(f"Words : {len(content.split()):,}")
    print()
    print(f"Top {MAX_RESULTS} words:")
    for rank, (word, count) in enumerate(top, 1):
        print(f"  {rank:>3}. {word:<20} {count:>6}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: app_with_bad_config.py <filepath>", file=sys.stderr)
        sys.exit(1)
    run_bad_config(sys.argv[1])

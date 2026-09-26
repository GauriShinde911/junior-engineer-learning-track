"""
main.py - Entry point for DataAuditor (target_app).
Accepts CLI flags, loads configuration, executes file audit, and reports results.
"""

import argparse
import json
import sys
from pathlib import Path

# Support running directly or as module
try:
    from .config import load_config
    from .logger import setup_logger
    from .processor import audit_directory
except ImportError:
    from config import load_config
    from logger import setup_logger
    from processor import audit_directory


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="DataAuditor",
        description="Audit directory contents, sizes, and file integrity digests."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to directory or file to audit (default: current directory)."
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Path to custom JSON configuration file."
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Path to write JSON audit report (default: stdout summary)."
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable DEBUG logging output."
    )
    parser.add_argument(
        "--version",
        action="version",
        version="DataAuditor 1.0.0"
    )
    return parser.parse_args(argv)


def run_app(argv=None) -> int:
    args = parse_args(argv)
    
    try:
        cfg = load_config(args.config)
    except Exception as e:
        sys.stderr.write(f"Error loading configuration: {e}\n")
        return 1

    log_level = "DEBUG" if args.verbose else cfg.get("log_level", "INFO")
    logger = setup_logger(log_level, log_to_file=cfg.get("log_to_file", True))
    logger.debug("Active configuration loaded from: %s", cfg.get("_loaded_from"))

    target_path = Path(args.target).resolve()
    try:
        report = audit_directory(
            target_path=target_path,
            allowed_extensions=cfg.get("allowed_extensions", []),
            max_file_size_mb=cfg.get("max_file_size_mb", 50),
            compute_hash=cfg.get("compute_hash", True)
        )
    except Exception as e:
        logger.error("Audit failure: %s", e)
        return 1

    if args.output:
        out_path = Path(args.output).resolve()
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            logger.info("Report successfully written to %s", out_path)
        except Exception as e:
            logger.error("Could not write output file: %s", e)
            return 1
    else:
        print("\n=== DATA AUDIT SUMMARY ===")
        print(f"Target:      {report['target']}")
        print(f"Total Files: {report['total_files']}")
        print(f"Total Bytes: {report['total_bytes']:,}")
        for item in report["files"]:
            digest_abbr = item["sha256"][:12] if item["sha256"] else "none"
            print(f" - {item['name']:<25} {item['size_bytes']:>8} bytes  (sha256: {digest_abbr}...)")
        print("==========================\n")

    return 0


if __name__ == "__main__":
    sys.exit(run_app())

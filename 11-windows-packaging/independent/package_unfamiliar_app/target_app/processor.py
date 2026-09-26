"""
Core processing engine for target_app.
Audits target paths and computes file size and cryptographic checksums.
"""

import hashlib
import logging
from pathlib import Path
from typing import Any, Dict, List


def hash_file(file_path: Path, chunk_size: int = 65536) -> str:
    """Compute SHA256 digest of a file."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def audit_directory(
    target_path: Path,
    allowed_extensions: List[str],
    max_file_size_mb: int,
    compute_hash: bool = True
) -> Dict[str, Any]:
    """Audit files matching criteria within a target directory."""
    logger = logging.getLogger("DataAuditor")
    logger.info("Scanning directory: %s", target_path)

    records = []
    total_bytes = 0
    max_bytes = max_file_size_mb * 1024 * 1024

    if not target_path.exists():
        raise FileNotFoundError(f"Directory not found: {target_path}")

    files_to_scan = [target_path] if target_path.is_file() else list(target_path.rglob("*"))

    for item in sorted(files_to_scan):
        if not item.is_file():
            continue

        if allowed_extensions and item.suffix.lower() not in [e.lower() for e in allowed_extensions]:
            logger.debug("Skipping unlisted extension: %s", item.name)
            continue

        size = item.stat().st_size
        if size > max_bytes:
            logger.warning("Skipping file exceeding limit (%d bytes): %s", size, item.name)
            continue

        digest = hash_file(item) if compute_hash else None
        records.append({
            "name": item.name,
            "path": str(item),
            "size_bytes": size,
            "sha256": digest
        })
        total_bytes += size

    logger.info("Audit completed. Total files: %d, Total bytes: %d", len(records), total_bytes)
    return {
        "target": str(target_path),
        "total_files": len(records),
        "total_bytes": total_bytes,
        "files": records
    }

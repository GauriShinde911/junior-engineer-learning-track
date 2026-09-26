"""
fixed_app/config.py - Application Configuration Loader (Fixed)

FIXES APPLIED:
1. Replaced brittle relative path with Path(__file__).resolve().parent / "data" / "catalog.json".
2. Coerced BATCH_LIMIT environment variable to integer with fallback handling.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


def get_batch_limit() -> int:
    """Returns the batch unit limit as a guaranteed integer."""
    raw = os.getenv("BATCH_LIMIT", "50")
    try:
        return int(raw)
    except ValueError:
        return 50


def load_catalog() -> Dict[str, Any]:
    """Loads product catalog safely regardless of process current working directory."""
    catalog_path = Path(__file__).resolve().parent / "data" / "catalog.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        return json.load(f)

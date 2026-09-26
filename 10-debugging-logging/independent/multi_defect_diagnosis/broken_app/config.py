"""
broken_app/config.py - Application Configuration Loader

PLANTED DEFECT 1:
1. Relative path assumption: Assumes CWD is broken_app/ directory. When run from repo root,
   open("data/catalog.json") crashes with FileNotFoundError.
2. Unparsed environment variable: os.getenv("BATCH_LIMIT", 50) returns string "25" when set,
   leading to comparison TypeErrors in pipeline batch validation.
"""

import os
import json
from typing import Dict, Any


def get_batch_limit() -> Any:
    # DEFECT 1B: If BATCH_LIMIT is set in environment, returns str instead of int
    return os.getenv("BATCH_LIMIT", 50)


def load_catalog() -> Dict[str, Any]:
    # DEFECT 1A: Hardcoded relative path fails unless process is run strictly from broken_app/
    catalog_path = "data/catalog.json"
    with open(catalog_path, "r", encoding="utf-8") as f:
        return json.load(f)

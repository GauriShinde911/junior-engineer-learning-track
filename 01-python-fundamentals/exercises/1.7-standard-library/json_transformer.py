"""
1.7 Standard Library: JSON Transformer
Demonstrates: json (loads, dumps, load, dump), pathlib.Path, schema filtering,
type normalization, and formatted serialization with indentation.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


def transform_records(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    min_age: int = 18
) -> List[Dict[str, Any]]:
    """
    Reads JSON records from input_path, standardizes field names,
    filters by min_age, and saves the cleaned records to output_path.
    """
    in_file = Path(input_path)
    out_file = Path(output_path)

    if not in_file.exists():
        raise FileNotFoundError(f"Source JSON file not found: {in_file}")

    with open(in_file, "r", encoding="utf-8") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError as err:
            raise ValueError(f"Invalid JSON in {in_file}: {err}")

    if not isinstance(records, list):
        raise TypeError("Expected root JSON element to be a list of objects.")

    transformed: List[Dict[str, Any]] = []
    for item in records:
        if not isinstance(item, dict):
            continue

        raw_age = item.get("age", 0)
        try:
            age = int(raw_age)
        except (ValueError, TypeError):
            continue

        # Filter criteria
        if age < min_age:
            continue

        full_name = str(item.get("name") or item.get("full_name") or "Unknown").strip()
        city = str(item.get("city", "N/A")).strip().title()

        transformed.append({
            "full_name": full_name,
            "age": age,
            "city": city,
            "is_adult": age >= 18
        })

    # Sort by age descending, then name ascending
    transformed.sort(key=lambda r: (-r["age"], r["full_name"]))

    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(transformed, f, indent=2)

    return transformed


if __name__ == "__main__":
    demo_in = Path("sample_records.json")
    demo_out = Path("transformed_records.json")

    sample_data = [
        {"name": "Alice Johnson", "age": 28, "city": "new york"},
        {"name": "Bobby Tables", "age": 14, "city": "boston"},
        {"name": "Charlie Davis", "age": 35, "city": "seattle"}
    ]
    demo_in.write_text(json.dumps(sample_data, indent=2), encoding="utf-8")

    result = transform_records(demo_in, demo_out, min_age=18)
    print(f"Transformed {len(result)} adult records to {demo_out}:")
    for r in result:
        print(f" - {r['full_name']} ({r['age']} yrs) | City: {r['city']}")

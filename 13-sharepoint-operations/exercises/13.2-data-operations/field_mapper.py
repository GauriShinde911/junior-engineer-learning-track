"""
field_mapper.py - Bidirectional Python <-> SharePoint Field Translation

Handles mapping between idiomatic Python dictionary keys/types and SharePoint
internal field names, date formatting, and type coercions.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional


class FieldDefinition:
    """Defines mapping constraints and conversions for a SharePoint field."""

    def __init__(
        self,
        internal_name: str,
        field_type: str = "text",
        required: bool = False,
        choices: Optional[List[str]] = None,
        default: Any = None,
    ):
        self.internal_name = internal_name
        self.field_type = field_type.lower()
        self.required = required
        self.choices = choices or []
        self.default = default


class SharePointFieldMapper:
    """
    Translates Python attribute dictionaries into SharePoint Graph API
    'fields' payloads and vice versa.
    """

    def __init__(self, schema_definition: Dict[str, FieldDefinition]):
        self.schema = schema_definition

    def to_sharepoint(self, python_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Python dictionary to SharePoint internal fields payload."""
        sp_payload = {}

        for py_key, field_def in self.schema.items():
            val = python_data.get(py_key, field_def.default)

            if field_def.required and (val is None or val == ""):
                raise ValueError(f"Required field '{py_key}' is missing or empty.")

            if val is None:
                continue

            # Validate choices
            if field_def.field_type == "choice" and field_def.choices:
                if str(val) not in field_def.choices:
                    raise ValueError(
                        f"Value '{val}' for field '{py_key}' not in allowed choices: {field_def.choices}"
                    )

            # Type conversions to SharePoint representation
            if field_def.field_type in ("date", "datetime"):
                if isinstance(val, (datetime, date)):
                    converted = val.strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(val, datetime) else val.strftime("%Y-%m-%d")
                elif isinstance(val, str):
                    converted = val
                else:
                    raise TypeError(f"Invalid date format for '{py_key}': {type(val)}")
                sp_payload[field_def.internal_name] = converted

            elif field_def.field_type in ("currency", "number"):
                if isinstance(val, (int, float, Decimal)):
                    sp_payload[field_def.internal_name] = float(val)
                elif isinstance(val, str):
                    try:
                        sp_payload[field_def.internal_name] = float(val)
                    except ValueError:
                        raise ValueError(f"Numeric field '{py_key}' cannot parse '{val}'")
                else:
                    raise TypeError(f"Invalid numeric value for '{py_key}'")

            elif field_def.field_type == "boolean":
                sp_payload[field_def.internal_name] = bool(val)

            else:  # text, multiline, etc.
                sp_payload[field_def.internal_name] = str(val)

        return sp_payload

    def to_python(self, sp_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Convert SharePoint Graph API fields dictionary back to Python types."""
        py_data = {}
        # Invert mapping: internal_name -> (py_key, field_def)
        inv_map = {f_def.internal_name: (k, f_def) for k, f_def in self.schema.items()}

        for sp_key, val in sp_fields.items():
            if sp_key in inv_map:
                py_key, field_def = inv_map[sp_key]
                if val is None:
                    py_data[py_key] = None
                    continue

                if field_def.field_type in ("date", "datetime"):
                    try:
                        # Parse ISO 8601 string
                        clean_str = val.replace("Z", "+00:00")
                        py_data[py_key] = datetime.fromisoformat(clean_str)
                    except (ValueError, TypeError):
                        py_data[py_key] = val
                elif field_def.field_type in ("currency", "number"):
                    try:
                        py_data[py_key] = float(val)
                    except (ValueError, TypeError):
                        py_data[py_key] = val
                elif field_def.field_type == "boolean":
                    py_data[py_key] = bool(val)
                else:
                    py_data[py_key] = val

        return py_data

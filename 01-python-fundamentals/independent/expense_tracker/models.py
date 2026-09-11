"""
Models module for CLI Expense Tracker.
Encapsulates Expense entity, validation rules, and serialization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class Expense:
    category: str
    amount: float
    date_str: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    description: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8].upper())

    def __post_init__(self):
        # Validation checks
        if not self.category or not str(self.category).strip():
            raise ValueError("Expense category cannot be empty.")
        self.category = str(self.category).strip().title()

        try:
            val = float(self.amount)
        except (ValueError, TypeError):
            raise ValueError(f"Amount must be a numeric value, got: '{self.amount}'")

        if val <= 0:
            raise ValueError(f"Amount must be strictly greater than 0, got: {val}")
        self.amount = round(val, 2)

        # Validate date format (YYYY-MM-DD)
        try:
            datetime.strptime(self.date_str.strip(), "%Y-%m-%d")
            self.date_str = self.date_str.strip()
        except ValueError:
            raise ValueError(f"Date must follow YYYY-MM-DD format, got: '{self.date_str}'")

        self.description = str(self.description).strip()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date_str,
            "category": self.category,
            "amount": self.amount,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Expense":
        return cls(
            id=str(data.get("id", uuid.uuid4().hex[:8].upper())),
            date_str=str(data.get("date", datetime.now().strftime("%Y-%m-%d"))),
            category=str(data.get("category", "")),
            amount=float(data.get("amount", 0.0)),
            description=str(data.get("description", ""))
        )

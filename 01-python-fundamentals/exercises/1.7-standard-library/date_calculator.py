"""
1.7 Standard Library: Date & Time Calculator
Demonstrates: datetime, timedelta, date parsing/formatting with strptime/strftime,
and business day calculations without external dependencies.
"""

from datetime import date, datetime, timedelta
from typing import Optional, Union


def days_between(date1_str: str, date2_str: str, fmt: str = "%Y-%m-%d") -> int:
    """Calculates absolute number of calendar days between two date strings."""
    d1 = datetime.strptime(date1_str.strip(), fmt)
    d2 = datetime.strptime(date2_str.strip(), fmt)
    return abs((d2 - d1).days)


def add_days(date_str: str, n_days: int, fmt: str = "%Y-%m-%d") -> str:
    """Adds N calendar days to a date string."""
    d = datetime.strptime(date_str.strip(), fmt)
    res = d + timedelta(days=n_days)
    return res.strftime(fmt)


def add_business_days(start_date_str: str, business_days: int, fmt: str = "%Y-%m-%d") -> str:
    """
    Adds N business days (Monday through Friday), skipping weekends.
    """
    current = datetime.strptime(start_date_str.strip(), fmt).date()
    added = 0
    step = 1 if business_days >= 0 else -1
    target = abs(business_days)

    while added < target:
        current += timedelta(days=step)
        # Monday is 0, Sunday is 6
        if current.weekday() < 5:
            added += 1

    return current.strftime(fmt)


def get_relative_time_description(date_str: str, reference_date: Optional[date] = None, fmt: str = "%Y-%m-%d") -> str:
    """Returns human-friendly relative label (e.g. 'today', '2 days ago', 'in 3 days')."""
    target = datetime.strptime(date_str.strip(), fmt).date()
    ref = reference_date or date.today()
    delta = (target - ref).days

    if delta == 0:
        return "today"
    elif delta == 1:
        return "tomorrow"
    elif delta == -1:
        return "yesterday"
    elif delta > 1:
        return f"in {delta} days"
    else:
        return f"{abs(delta)} days ago"


if __name__ == "__main__":
    start = "2026-01-01"
    end = "2026-01-15"
    print("=== Date Calculator Demo ===")
    print(f"Calendar days between {start} and {end}: {days_between(start, end)} days")
    print(f"5 business days after Friday 2026-01-02: {add_business_days('2026-01-02', 5)}")
    print(f"30 days from {start}: {add_days(start, 30)}")

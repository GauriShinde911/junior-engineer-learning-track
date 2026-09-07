from datetime import datetime, timedelta

# calculates the absolute number of days between two date strings (YYYY-MM-DD)
def days_between(date1_str, date2_str):
    d1 = datetime.strptime(date1_str, "%Y-%m-%d")
    d2 = datetime.strptime(date2_str, "%Y-%m-%d")
    diff = abs((d2 - d1).days)
    return diff

# adds N days to a date string (YYYY-MM-DD) and returns the new date string
def add_days(date_str, n_days):
    d = datetime.strptime(date_str, "%Y-%m-%d")
    new_date = d + timedelta(days=n_days)
    return new_date.strftime("%Y-%m-%d")

if __name__ == "__main__":
    start = "2026-01-01"
    end = "2026-01-15"
    
    print("=== Date Calculator Demo ===")
    print(f"Start date: {start}")
    print(f"End date:   {end}")
    
    days = days_between(start, end)
    print(f"Days between: {days} days")
    
    future_date = add_days(start, 30)
    print(f"30 days after {start}: {future_date}")

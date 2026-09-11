"""
1.1 Syntax & Execution: Unit Converter
Demonstrates: Numerical conversions, constants, formatted string output (f-strings),
and graceful validation of non-numeric input and impossible physical values.
"""

# Conversion factors
KM_TO_MILES_FACTOR = 0.621371
KG_TO_LBS_FACTOR = 2.20462


def km_to_miles(km: float) -> float:
    if km < 0:
        raise ValueError("Distance in kilometers cannot be negative.")
    return km * KM_TO_MILES_FACTOR


def miles_to_km(miles: float) -> float:
    if miles < 0:
        raise ValueError("Distance in miles cannot be negative.")
    return miles / KM_TO_MILES_FACTOR


def celsius_to_fahrenheit(celsius: float) -> float:
    if celsius < -273.15:
        raise ValueError("Temperature cannot be below absolute zero (-273.15°C).")
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    if fahrenheit < -459.67:
        raise ValueError("Temperature cannot be below absolute zero (-459.67°F).")
    return (fahrenheit - 32) * 5 / 9


def run_cli():
    print("=== Unit Converter ===")
    print("1. Kilometers to Miles")
    print("2. Miles to Kilometers")
    print("3. Celsius to Fahrenheit")
    print("4. Fahrenheit to Celsius")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        choice = input("Choose an option (1-4 or exit): ").strip()
        if choice.lower() in ("exit", "quit"):
            print("Exiting converter. Bye!")
            break

        if choice not in ("1", "2", "3", "4"):
            print("Invalid selection. Please enter 1, 2, 3, 4, or exit.\n")
            continue

        raw_val = input("Enter value to convert: ").strip()
        try:
            val = float(raw_val)
        except ValueError:
            print(f"Error: '{raw_val}' is not a valid number.\n")
            continue

        try:
            if choice == "1":
                res = km_to_miles(val)
                print(f"{val:.2f} km = {res:.2f} miles\n")
            elif choice == "2":
                res = miles_to_km(val)
                print(f"{val:.2f} miles = {res:.2f} km\n")
            elif choice == "3":
                res = celsius_to_fahrenheit(val)
                print(f"{val:.2f}°C = {res:.2f}°F\n")
            elif choice == "4":
                res = fahrenheit_to_celsius(val)
                print(f"{val:.2f}°F = {res:.2f}°C\n")
        except ValueError as err:
            print(f"Validation Error: {err}\n")


if __name__ == "__main__":
    run_cli()

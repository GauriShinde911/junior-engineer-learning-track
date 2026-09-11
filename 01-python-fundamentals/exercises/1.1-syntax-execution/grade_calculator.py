"""
1.1 Syntax & Execution: Grade Calculator
Demonstrates: Numeric input, comparisons, conditional evaluation, and boundary validation.
"""

def get_letter_grade(score: float) -> str:
    """
    Map a percentage score (0-100) to a letter grade.
    Raises ValueError if score is outside [0, 100].
    """
    if score < 0 or score > 100:
        raise ValueError(f"Score must be between 0 and 100 inclusive. Received: {score}")

    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def run_cli():
    print("=== Academic Grade Calculator ===")
    user_input = input("Enter your percentage score (0-100): ").strip()

    # Graceful handling of non-numeric or out-of-range input
    try:
        score = float(user_input)
        grade = get_letter_grade(score)
        print(f"Score: {score:.1f}% -> Final Grade: {grade}")
    except ValueError as err:
        print(f"Input Error: {err}")


if __name__ == "__main__":
    run_cli()

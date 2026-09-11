"""
1.2 Control Flow: Number Analysis
Demonstrates: for loops, range(), break, continue, conditional expressions,
and calculating aggregated summary metrics.
"""

def is_prime(n: int) -> bool:
    """Check if an integer >= 2 is prime using trial division."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False  # Early exit via return
    return True


def analyze_numbers(numbers: list) -> dict:
    """
    Analyze a list of numbers using iteration and conditional logic.
    Returns statistical metrics and filtered sets.
    """
    if not numbers:
        return {
            "count": 0,
            "sum": 0,
            "average": 0.0,
            "max": None,
            "min": None,
            "even_count": 0,
            "odd_count": 0,
            "primes": []
        }

    total = 0
    even_count = 0
    odd_count = 0
    primes = []
    maximum = numbers[0]
    minimum = numbers[0]

    for num in numbers:
        # Ignore non-integers or floats gracefully
        if not isinstance(num, (int, float)):
            continue

        total += num
        if num > maximum:
            maximum = num
        if num < minimum:
            minimum = num

        # Conditional parity counting
        if int(num) == num:
            int_val = int(num)
            if int_val % 2 == 0:
                even_count += 1
            else:
                odd_count += 1

            if is_prime(int_val):
                primes.append(int_val)

    count = len(numbers)
    avg = round(total / count, 2) if count > 0 else 0.0

    return {
        "count": count,
        "sum": total,
        "average": avg,
        "max": maximum,
        "min": minimum,
        "even_count": even_count,
        "odd_count": odd_count,
        "primes": primes
    }


if __name__ == "__main__":
    test_data = [12, 7, 3, 18, 25, 11, 4, 2, 9, 31]
    print("Input numbers:", test_data)

    stats = analyze_numbers(test_data)
    print("\n--- Number Analysis Report ---")
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title():<15}: {value}")

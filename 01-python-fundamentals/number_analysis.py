# checks if a positive integer is a prime number
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

# analyzes a list of numbers and returns key statistics
def analyze_numbers(numbers):
    if not numbers:
        return None
        
    total = sum(numbers)
    avg = total / len(numbers)
    maximum = max(numbers)
    minimum = min(numbers)
    
    even_count = 0
    odd_count = 0
    primes = []
    
    for num in numbers:
        if num % 2 == 0:
            even_count += 1
        else:
            odd_count += 1
            
        if is_prime(num):
            primes.append(num)
            
    return {
        "count": len(numbers),
        "sum": total,
        "average": round(avg, 2),
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
    print(f"Total count:   {stats['count']}")
    print(f"Sum:           {stats['sum']}")
    print(f"Average:       {stats['average']}")
    print(f"Max value:     {stats['max']}")
    print(f"Min value:     {stats['min']}")
    print(f"Even numbers:  {stats['even_count']}")
    print(f"Odd numbers:   {stats['odd_count']}")
    print(f"Prime numbers: {stats['primes']}")

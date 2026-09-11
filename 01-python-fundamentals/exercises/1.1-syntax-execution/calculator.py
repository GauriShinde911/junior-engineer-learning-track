"""
1.1 Syntax & Execution: Basic Arithmetic Calculator
Demonstrates: Variables, numerical types (int, float), expressions, operators,
input/output, type casting, error handling for non-numeric and division by zero.
"""

def calculate(num1: float, num2: float, operation: str):
    """Perform arithmetic operation between two numbers."""
    if operation == "+":
        return num1 + num2
    elif operation == "-":
        return num1 - num2
    elif operation == "*":
        return num1 * num2
    elif operation == "/":
        if num2 == 0:
            return "Error: Cannot divide by zero"
        return num1 / num2
    elif operation == "%":
        if num2 == 0:
            return "Error: Modulo by zero is undefined"
        return num1 % num2
    else:
        return f"Error: Invalid operation '{operation}'"


def run_cli():
    print("=== Simple Calculator ===")
    print("Available operations: +, -, *, /, %")
    print("Type 'quit' at any prompt to exit.\n")

    while True:
        op = input("Enter operation (+, -, *, /, %) or 'quit': ").strip()
        if op.lower() == "quit":
            print("Exiting calculator. Goodbye!")
            break

        if op not in ("+", "-", "*", "/", "%"):
            print(f"Invalid operation '{op}'. Please choose +, -, *, /, or %.\n")
            continue

        raw_n1 = input("Enter first number: ").strip()
        if raw_n1.lower() == "quit":
            break
        raw_n2 = input("Enter second number: ").strip()
        if raw_n2.lower() == "quit":
            break

        # Negative / invalid input handling
        try:
            n1 = float(raw_n1)
            n2 = float(raw_n2)
        except ValueError:
            print("Error: Both inputs must be valid numeric values.\n")
            continue

        result = calculate(n1, n2, op)
        print(f"Result: {n1} {op} {n2} = {result}\n")


if __name__ == "__main__":
    run_cli()

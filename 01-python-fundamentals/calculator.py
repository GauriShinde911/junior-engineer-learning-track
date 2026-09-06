# performs basic arithmetic on two numbers
def calculate(num1, num2, operation):
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
    else:
        return "Error: Invalid operation"

if __name__ == "__main__":
    print("Simple Calculator")
    print("Type 'quit' to stop\n")
    
    while True:
        user_choice = input("Enter operation (+, -, *, /) or 'quit': ")
        if user_choice.lower() == "quit":
            print("Goodbye!")
            break
            
        n1 = float(input("Enter first number: "))
        n2 = float(input("Enter second number: "))
        
        result = calculate(n1, n2, user_choice)
        print("Result:", result)
        print()

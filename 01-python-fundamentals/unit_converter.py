# converts kilometers to miles
def km_to_miles(km):
    return km * 0.621371

# converts miles to kilometers
def miles_to_km(miles):
    return miles / 0.621371

# converts celsius to fahrenheit
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# converts fahrenheit to celsius
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

if __name__ == "__main__":
    while True:
        print("\n--- Unit Converter ---")
        print("1. Kilometers to Miles")
        print("2. Miles to Kilometers")
        print("3. Celsius to Fahrenheit")
        print("4. Fahrenheit to Celsius")
        print("Type 'exit' to quit")
        
        choice = input("\nChoose an option (1-4 or exit): ")
        
        if choice.lower() == "exit":
            print("Exiting converter. Bye!")
            break
            
        if choice == "1":
            km = float(input("Enter kilometers: "))
            print(f"{km} km = {km_to_miles(km):.2f} miles")
        elif choice == "2":
            miles = float(input("Enter miles: "))
            print(f"{miles} miles = {miles_to_km(miles):.2f} km")
        elif choice == "3":
            c = float(input("Enter temperature in Celsius: "))
            print(f"{c}°C = {celsius_to_fahrenheit(c):.2f}°F")
        elif choice == "4":
            f = float(input("Enter temperature in Fahrenheit: "))
            print(f"{f}°F = {fahrenheit_to_celsius(f):.2f}°C")
        else:
            print("Invalid option, please try again.")

# sample employee records
employees = [
    {"name": "Alice Johnson", "dept": "Engineering", "salary": 75000},
    {"name": "Bob Smith", "dept": "Marketing", "salary": 58000},
    {"name": "Charlie Brown", "dept": "Engineering", "salary": 82000},
    {"name": "Diana Prince", "dept": "HR", "salary": 62000}
]

# adds a new employee record and returns a new updated list
def add_employee(directory, name, dept, salary):
    new_directory = directory.copy()  # proper copy so original list isn't mutated unexpectedly
    new_employee = {"name": name, "dept": dept, "salary": salary}
    new_directory.append(new_employee)
    return new_directory

# searches for an employee by name (case-insensitive)
def find_employee_by_name(directory, name):
    for emp in directory:
        if emp["name"].lower() == name.lower():
            return emp
    return None

# calculates the average salary across all employees
def calculate_average_salary(directory):
    if not directory:
        return 0.0
    total_salary = 0
    for emp in directory:
        total_salary = total_salary + emp["salary"]
    return total_salary / len(directory)

# --- COMMON MISTAKE DEMO: Reference Alias vs Actual Copy ---
def demonstrate_alias_bug():
    print("--- Common Mistake: Reference vs Copy ---")
    original_list = ["Alice", "Bob"]
    
    # BUG: This does NOT copy the list! 'alias_list' points to the exact same object in memory.
    alias_list = original_list
    alias_list.append("Charlie")
    
    print("After appending to alias_list:")
    print("alias_list:   ", alias_list)
    print("original_list:", original_list)  # original_list also changed!
    
    # FIX: Use .copy() or list() to create an independent shallow copy.
    safe_copy = original_list.copy()
    safe_copy.append("Diana")
    print("\nAfter using .copy():")
    print("safe_copy:    ", safe_copy)
    print("original_list:", original_list)  # original_list remains unchanged

if __name__ == "__main__":
    print("Average Salary: $", calculate_average_salary(employees))
    
    match = find_employee_by_name(employees, "alice johnson")
    print("Found:", match)
    
    updated = add_employee(employees, "Eve Adams", "Sales", 65000)
    print("Total employees after add:", len(updated))
    print()
    demonstrate_alias_bug()

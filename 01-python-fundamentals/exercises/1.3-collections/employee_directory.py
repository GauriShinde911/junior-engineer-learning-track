"""
1.3 Collections: Employee Directory
Demonstrates: Nested dictionaries, tuples, sets (unique elements),
comprehensions, and critical difference between reference aliasing vs shallow/deep copying.
"""

import copy

EMPLOYEES = [
    {"id": (101, "ENG"), "name": "Alice Johnson", "dept": "Engineering", "salary": 75000},
    {"id": (102, "MKT"), "name": "Bob Smith", "dept": "Marketing", "salary": 58000},
    {"id": (103, "ENG"), "name": "Charlie Brown", "dept": "Engineering", "salary": 82000},
    {"id": (104, "HR"),  "name": "Diana Prince", "dept": "HR", "salary": 62000}
]


def get_unique_departments(directory: list) -> set:
    """Extract a set of all unique department names (O(1) lookups)."""
    return {emp["dept"] for emp in directory}


def calculate_average_salary(directory: list) -> float:
    """Calculate mean salary across all employees."""
    if not directory:
        return 0.0
    total = sum(emp["salary"] for emp in directory)
    return round(total / len(directory), 2)


def find_employee_by_name(directory: list, name: str):
    """Linear search for employee by name (case-insensitive)."""
    target = name.strip().lower()
    for emp in directory:
        if emp["name"].strip().lower() == target:
            return emp
    return None


def safe_add_employee(directory: list, emp_id: tuple, name: str, dept: str, salary: float) -> list:
    """
    Creates a new directory list without mutating the original input.
    Uses deepcopy to protect nested dictionaries.
    """
    new_dir = copy.deepcopy(directory)
    new_dir.append({
        "id": emp_id,
        "name": name.strip(),
        "dept": dept.strip(),
        "salary": float(salary)
    })
    return new_dir


def demonstrate_mutation_vs_copy():
    """
    Educational demonstration of reference assignment vs shallow vs deep copy.
    """
    original = [{"name": "Alice", "skills": ["Python"]}]

    # 1. Reference Alias (Points to the exact same memory location)
    alias = original
    alias[0]["name"] = "Alice Edited"
    alias_same = original[0]["name"] == "Alice Edited"

    # Reset
    original[0]["name"] = "Alice"

    # 2. Shallow Copy (.copy() or list())
    shallow = original.copy()
    shallow.append({"name": "Bob", "skills": ["SQL"]})
    # Appending to shallow does NOT affect original list length:
    len_diverged = len(shallow) != len(original)
    # BUT nested objects inside shallow still reference original objects:
    shallow[0]["skills"].append("Docker")
    nested_mutated = "Docker" in original[0]["skills"]

    # 3. Deep Copy
    deep = copy.deepcopy(original)
    deep[0]["skills"].append("Kubernetes")
    deep_isolated = "Kubernetes" not in original[0]["skills"]

    return {
        "alias_mutates_original": alias_same,
        "shallow_list_length_isolated": len_diverged,
        "shallow_nested_still_shared": nested_mutated,
        "deep_copy_fully_isolated": deep_isolated
    }


if __name__ == "__main__":
    print("=== Employee Directory Demo ===")
    print("Unique Departments:", get_unique_departments(EMPLOYEES))
    print(f"Average Salary: ${calculate_average_salary(EMPLOYEES):,.2f}")

    found = find_employee_by_name(EMPLOYEES, "Alice Johnson")
    print("Found employee:", found)

    print("\n--- Mutability Experiment Results ---")
    results = demonstrate_mutation_vs_copy()
    for test, passed in results.items():
        print(f"{test}: {passed}")

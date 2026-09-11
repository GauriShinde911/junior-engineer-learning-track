"""
1.2 Control Flow: Pattern Generation
Demonstrates: Nested loops, range() stepping, string repetition, and loop indexing.
"""

def generate_right_triangle(rows: int, char: str = "*") -> list:
    """Generate lines of a right-angled triangle pattern."""
    if rows <= 0:
        return []
    lines = []
    for i in range(1, rows + 1):
        row_str = ""
        for _ in range(i):
            row_str += char
        lines.append(row_str)
    return lines


def generate_centered_pyramid(rows: int, char: str = "*") -> list:
    """Generate lines of a centered pyramid pattern with spaces."""
    if rows <= 0:
        return []
    lines = []
    for i in range(1, rows + 1):
        spaces = " " * (rows - i)
        chars = char * (2 * i - 1)
        lines.append(f"{spaces}{chars}")
    return lines


def generate_number_staircase(rows: int) -> list:
    """Generate a numeric staircase (e.g. 1, 12, 123)."""
    if rows <= 0:
        return []
    lines = []
    for i in range(1, rows + 1):
        row_str = ""
        for j in range(1, i + 1):
            row_str += str(j)
        lines.append(row_str)
    return lines


if __name__ == "__main__":
    print("=== Right Triangle (5 rows) ===")
    print("\n".join(generate_right_triangle(5)))

    print("\n=== Centered Pyramid (5 rows) ===")
    print("\n".join(generate_centered_pyramid(5)))

    print("\n=== Number Staircase (5 rows) ===")
    print("\n".join(generate_number_staircase(5)))

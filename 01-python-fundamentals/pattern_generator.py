# prints a right-angled triangle pattern of stars using nested loops
def print_triangle(rows):
    for i in range(1, rows + 1):
        line = ""
        for j in range(i):
            line = line + "*"
        print(line)

if __name__ == "__main__":
    num_rows = int(input("Enter number of rows for triangle: "))
    print_triangle(num_rows)

# converts a percentage score into a letter grade
def get_letter_grade(score):
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

if __name__ == "__main__":
    user_input = input("Enter your score (0-100): ")
    score = float(user_input)
    grade = get_letter_grade(score)
    print("Your grade is:", grade)

# converts text to all uppercase letters
def to_upper(text):
    return text.upper()

# converts text to all lowercase letters
def to_lower(text):
    return text.lower()

# capitalizes the first letter of each word
def to_title(text):
    return text.title()

# reverses the entire text string
def reverse_text(text):
    return text[::-1]

if __name__ == "__main__":
    print("=== Text Formatter ===")
    user_text = input("Enter a sentence to format: ")
    
    while True:
        print(f"\nCurrent text: \"{user_text}\"")
        print("1. Uppercase")
        print("2. Lowercase")
        print("3. Title Case")
        print("4. Reverse Text")
        print("5. Enter New Sentence")
        print("6. Exit")
        
        choice = input("\nChoose an option (1-6): ")
        
        if choice == "1":
            print("Result:", to_upper(user_text))
        elif choice == "2":
            print("Result:", to_lower(user_text))
        elif choice == "3":
            print("Result:", to_title(user_text))
        elif choice == "4":
            print("Result:", reverse_text(user_text))
        elif choice == "5":
            user_text = input("Enter new sentence: ")
        elif choice == "6":
            print("Exiting formatter. Bye!")
            break
        else:
            print("Invalid option, please choose between 1 and 6.")

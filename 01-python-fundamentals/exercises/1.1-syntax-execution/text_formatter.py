"""
1.1 Syntax & Execution: Text Formatter
Demonstrates: String methods, slicing, type inspection, interactive options,
and graceful handling of blank/whitespace-only input.
"""

def to_upper(text: str) -> str:
    return text.upper()


def to_lower(text: str) -> str:
    return text.lower()


def to_title(text: str) -> str:
    return text.title()


def reverse_text(text: str) -> str:
    return text[::-1]


def count_words(text: str) -> int:
    return len(text.split())


def run_cli():
    print("=== Text Formatter CLI ===")
    user_text = input("Enter an initial sentence: ").strip()
    if not user_text:
        print("Notice: You entered empty text. Initializing to default 'Hello, Python!'.")
        user_text = "Hello, Python!"

    while True:
        print(f"\nCurrent string: \"{user_text}\"")
        print("1. Convert to UPPERCASE")
        print("2. Convert to lowercase")
        print("3. Convert to Title Case")
        print("4. Reverse text")
        print("5. Word count")
        print("6. Enter new sentence")
        print("7. Exit")

        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            print("Result:", to_upper(user_text))
        elif choice == "2":
            print("Result:", to_lower(user_text))
        elif choice == "3":
            print("Result:", to_title(user_text))
        elif choice == "4":
            print("Result:", reverse_text(user_text))
        elif choice == "5":
            print("Word count:", count_words(user_text))
        elif choice == "6":
            new_sentence = input("Enter new sentence: ").strip()
            if not new_sentence:
                print("Error: Sentence cannot be completely empty.")
            else:
                user_text = new_sentence
        elif choice == "7":
            print("Exiting formatter. Bye!")
            break
        else:
            print("Invalid option. Please choose between 1 and 7.")


if __name__ == "__main__":
    run_cli()

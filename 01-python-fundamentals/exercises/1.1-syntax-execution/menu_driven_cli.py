"""
1.1 Syntax & Execution: Menu-Driven CLI Notes Manager
Demonstrates: Command-line menus, user input branching, in-memory list operations,
and defensive handling of non-integer or out-of-range selection numbers.
"""

def add_note(notes: list, note_text: str) -> bool:
    cleaned = note_text.strip()
    if not cleaned:
        raise ValueError("Cannot add an empty note.")
    notes.append(cleaned)
    return True


def view_notes(notes: list) -> list:
    return list(notes)


def delete_note(notes: list, index: int) -> str:
    """Deletes a note by 1-based index."""
    if not isinstance(index, int):
        raise TypeError("Note index must be an integer.")
    if index < 1 or index > len(notes):
        raise IndexError(f"Invalid note index: {index}. Range is 1 to {len(notes)}.")
    return notes.pop(index - 1)


def run_cli():
    notes = []
    print("=== Simple Notes Manager CLI ===")

    while True:
        print("\nMenu:")
        print("1. Add note")
        print("2. View notes")
        print("3. Delete note")
        print("4. Exit")

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            text = input("Enter your note: ")
            try:
                add_note(notes, text)
                print("Note added successfully.")
            except ValueError as err:
                print(f"Error: {err}")

        elif choice == "2":
            all_notes = view_notes(notes)
            if not all_notes:
                print("No notes recorded yet.")
            else:
                print("\n--- Current Notes ---")
                for i, item in enumerate(all_notes, start=1):
                    print(f"{i}. {item}")

        elif choice == "3":
            if not notes:
                print("No notes to delete.")
                continue
            for i, item in enumerate(notes, start=1):
                print(f"{i}. {item}")
            raw_idx = input("Enter note number to delete: ").strip()
            try:
                idx = int(raw_idx)
                removed = delete_note(notes, idx)
                print(f"Deleted note #{idx}: '{removed}'")
            except ValueError:
                print(f"Error: '{raw_idx}' is not a valid integer number.")
            except IndexError as err:
                print(f"Error: {err}")

        elif choice == "4":
            print("Exiting Notes Manager. Goodbye!")
            break
        else:
            print(f"Invalid choice '{choice}'. Please enter a number between 1 and 4.")


if __name__ == "__main__":
    run_cli()

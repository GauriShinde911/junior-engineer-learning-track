# adds a new note to the in-memory list
def add_note(notes, note_text):
    notes.append(note_text)
    print("Note added successfully!")

# prints all saved notes with their index numbers
def view_notes(notes):
    if not notes:
        print("No notes found.")
        return
    print("\n--- Your Notes ---")
    for i in range(len(notes)):
        print(f"{i + 1}. {notes[i]}")

# deletes a note by its 1-based index number
def delete_note(notes, index):
    if index < 1 or index > len(notes):
        print("Invalid note number.")
        return
    removed = notes.pop(index - 1)
    print(f"Deleted: '{removed}'")

if __name__ == "__main__":
    notes_list = []
    
    while True:
        print("\n=== Simple Notes Manager ===")
        print("1. Add note")
        print("2. View notes")
        print("3. Delete note")
        print("4. Exit")
        
        choice = input("\nChoose an option (1-4): ")
        
        if choice == "1":
            text = input("Enter your note: ")
            if text.strip():
                add_note(notes_list, text.strip())
            else:
                print("Cannot add an empty note.")
        elif choice == "2":
            view_notes(notes_list)
        elif choice == "3":
            view_notes(notes_list)
            if notes_list:
                num = int(input("Enter note number to delete: "))
                delete_note(notes_list, num)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please enter 1, 2, 3, or 4.")

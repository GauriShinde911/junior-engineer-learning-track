"""
1.2 Control Flow: Interactive Menu Loop
Demonstrates: while True loops, break, continue, sentinel values,
conditional expressions, and input retry validation patterns.
"""

def execute_action(choice: str, state: dict) -> bool:
    """
    Execute an action based on choice. Returns True to continue, False to terminate.
    """
    if choice == "1":
        state["counter"] += 1
        status = "positive" if state["counter"] > 0 else "neutral or negative"
        print(f"Counter incremented to: {state['counter']} (Status: {status})")
    elif choice == "2":
        state["counter"] -= 1
        status = "positive" if state["counter"] > 0 else "neutral or negative"
        print(f"Counter decremented to: {state['counter']} (Status: {status})")
    elif choice == "3":
        state["counter"] = 0
        print("Counter reset to 0.")
    elif choice == "4":
        print(f"Current State: Counter = {state['counter']}, Iterations = {state['iterations']}")
    elif choice == "5":
        print("Received exit command. Terminating menu loop.")
        return False
    else:
        print(f"Unknown choice '{choice}'. Please pick between 1 and 5.")
    return True


def run_menu(simulated_inputs: list = None):
    """
    Runs the menu loop. If simulated_inputs is passed (e.g. in tests),
    it consumes items from the list; otherwise prompts with input().
    """
    state = {"counter": 0, "iterations": 0}
    input_iter = iter(simulated_inputs) if simulated_inputs is not None else None

    print("=== State Manager Menu Loop ===")
    while True:
        state["iterations"] += 1

        if input_iter is not None:
            try:
                choice = next(input_iter).strip()
            except StopIteration:
                break
        else:
            print("\nOptions: [1] Increment  [2] Decrement  [3] Reset  [4] View State  [5] Exit")
            choice = input("Enter choice (1-5): ").strip()

        # Guard against blank input using continue
        if not choice:
            print("Notice: Empty input detected. Retrying...")
            continue

        should_continue = execute_action(choice, state)
        if not should_continue:
            break

    return state


if __name__ == "__main__":
    run_menu()

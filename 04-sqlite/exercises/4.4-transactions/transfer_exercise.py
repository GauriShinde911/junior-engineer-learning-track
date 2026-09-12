"""
4.4 Transactions: transfer_exercise.py
Demonstrates atomic transactions using commit and rollback for financial fund transfers.
Includes explicit failure simulation proving that failed transactions leave balances untouched.
"""

from dataclasses import dataclass
from pathlib import Path
import sqlite3


@dataclass
class Account:
    id: int
    owner: str
    balance: float


def init_accounts_table(conn: sqlite3.Connection) -> None:
    """Initializes the bank accounts table with sample accounts."""
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("""
        DROP TABLE IF EXISTS accounts;
    """)
    conn.execute("""
        CREATE TABLE accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            balance REAL NOT NULL CHECK (balance >= 0.0)
        );
    """)
    conn.executemany(
        "INSERT INTO accounts (owner, balance) VALUES (?, ?);",
        [
            ("Alice Green", 500.00),
            ("Bob Vance", 250.00),
            ("Charlie Brown", 50.00),
        ],
    )
    conn.commit()


def get_account(conn: sqlite3.Connection, account_id: int) -> Account | None:
    """Fetches an account balance by ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT id, owner, balance FROM accounts WHERE id = ?;", (account_id,))
    row = cursor.fetchone()
    if row:
        return Account(row[0], row[1], float(row[2]))
    return None


def transfer_funds(
    conn: sqlite3.Connection,
    from_account_id: int,
    to_account_id: int,
    amount: float,
    simulate_failure: bool = False,
) -> bool:
    """
    Transfers funds atomically between two accounts.
    Steps:
      1. Validate amount and verify sender has sufficient balance.
      2. Begin transaction block.
      3. Debit sender account.
      4. If simulate_failure is True, raise an exception midway.
      5. Credit recipient account.
      6. Commit transaction.
    If an exception occurs at any point, rollback() is invoked, preserving state.
    """
    if amount <= 0:
        raise ValueError(f"Transfer amount must be positive. Received: {amount}")

    if from_account_id == to_account_id:
        raise ValueError("Cannot transfer funds to the same account.")

    # Explicit transaction management
    # SQLite connection in Python defaults to managing transactions, but explicit control is clearest
    cursor = conn.cursor()

    try:
        # Check source account
        sender = get_account(conn, from_account_id)
        recipient = get_account(conn, to_account_id)

        if not sender:
            raise ValueError(f"Sender account ID {from_account_id} not found.")
        if not recipient:
            raise ValueError(f"Recipient account ID {to_account_id} not found.")
        if sender.balance < amount:
            raise ValueError(
                f"Insufficient funds: {sender.owner} has ${sender.balance:.2f}, requested ${amount:.2f}"
            )

        # Step 1: Debit sender
        cursor.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?;",
            (amount, from_account_id),
        )

        # Step 2: Simulate failure condition midway (e.g., network disconnect, crash)
        if simulate_failure:
            raise RuntimeError(
                "SIMULATED SYSTEM CRASH: Network failure during transfer processing!"
            )

        # Step 3: Credit recipient
        cursor.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?;",
            (amount, to_account_id),
        )

        # Step 4: Commit atomic changes
        conn.commit()
        return True

    except Exception as err:
        conn.rollback()
        raise err


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    init_accounts_table(conn)

    print("--- Initial Account Balances ---")
    for acc_id in [1, 2, 3]:
        acc = get_account(conn, acc_id)
        print(f"Account {acc.id} ({acc.owner}): ${acc.balance:.2f}")

    # Case 1: Successful Transfer ($100 from Alice to Bob)
    print("\nExecuting Happy Path: Transferring $100.00 from Alice (1) to Bob (2)...")
    success = transfer_funds(conn, from_account_id=1, to_account_id=2, amount=100.00)
    print(f"Transfer Success: {success}")
    print(f"Alice balance: ${get_account(conn, 1).balance:.2f}")
    print(f"Bob balance:   ${get_account(conn, 2).balance:.2f}")

    # Case 2: Deliberately Triggered Failure midway
    print("\nExecuting Failure Simulation: Transferring $50.00 from Bob (2) to Charlie (3) with failure...")
    try:
        transfer_funds(conn, from_account_id=2, to_account_id=3, amount=50.00, simulate_failure=True)
    except RuntimeError as ex:
        print(f"Caught expected error: {ex}")

    print("\nVerifying Balances After Rollback (Must remain identical to pre-failure values):")
    print(f"Bob balance:     ${get_account(conn, 2).balance:.2f} (Expected: 350.00)")
    print(f"Charlie balance: ${get_account(conn, 3).balance:.2f} (Expected: 50.00)")

    conn.close()

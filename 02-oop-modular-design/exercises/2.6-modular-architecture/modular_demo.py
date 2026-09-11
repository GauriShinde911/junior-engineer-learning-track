"""
Exercise 2.6: Modular Architecture — Library Book Checkout System

Demonstrates the Domain → Service → Repository three-layer split
inside a single file (each layer clearly labelled).

WHY DOES BUSINESS LOGIC NOT DEPEND ON HOW DATA IS STORED?
---------------------------------------------------------
LibraryService only imports:
  - Domain classes (Book, Member) — pure data, no I/O
  - BookRepository (ABC)         — an interface, not an implementation

This means:
  1. You can swap InMemoryBookRepository for a SQLite or REST-API
     implementation and LibraryService requires ZERO changes.
  2. Unit tests inject a fake/mock repository — no file system, no
     database, no network. Tests stay fast and deterministic.
  3. Each layer has a single reason to change:
     - Domain changes  → only domain layer affected
     - Business rules  → only service layer affected
     - Storage backend → only repository layer affected
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import date, timedelta


# =====================================================================
# LAYER 1 — DOMAIN
# Pure data objects + business rules. No I/O. No imports from layers 2/3.
# =====================================================================
class BookNotAvailableError(Exception):
    """Raised when a checkout is attempted on an unavailable book."""


class MemberNotFoundError(KeyError):
    """Raised when a member ID cannot be resolved."""


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    available: bool = True

    def mark_checked_out(self) -> None:
        if not self.available:
            raise BookNotAvailableError(f"'{self.title}' is already checked out.")
        self.available = False

    def mark_returned(self) -> None:
        self.available = True

    def __repr__(self) -> str:
        status = "available" if self.available else "checked out"
        return f"Book('{self.title}' by {self.author} [{status}])"


@dataclass
class Member:
    member_id: str
    name: str
    checked_out_isbns: List[str] = field(default_factory=list)

    def can_checkout(self) -> bool:
        return len(self.checked_out_isbns) < 3  # business rule: max 3 books

    def __repr__(self) -> str:
        return f"Member('{self.name}', books_held={len(self.checked_out_isbns)})"


@dataclass
class CheckoutRecord:
    member_id: str
    isbn: str
    checkout_date: date
    due_date: date = field(init=False)

    def __post_init__(self):
        self.due_date = self.checkout_date + timedelta(days=14)  # 2-week loan period


# =====================================================================
# LAYER 2 — REPOSITORY (interface + implementations)
# Data access only. LibraryService depends on BookRepository ABC, never
# on InMemoryBookRepository directly.
# =====================================================================
class BookRepository(ABC):
    """Interface contract for book and member data access."""

    @abstractmethod
    def get_book(self, isbn: str) -> Optional[Book]: ...

    @abstractmethod
    def save_book(self, book: Book) -> None: ...

    @abstractmethod
    def get_member(self, member_id: str) -> Optional[Member]: ...

    @abstractmethod
    def save_member(self, member: Member) -> None: ...

    @abstractmethod
    def save_checkout_record(self, record: CheckoutRecord) -> None: ...

    @abstractmethod
    def list_books(self) -> List[Book]: ...


class InMemoryBookRepository(BookRepository):
    """
    Stores all data in plain Python dicts — ideal for unit tests.
    Swap this for a SQLite or REST implementation without touching LibraryService.
    """

    def __init__(self):
        self._books: Dict[str, Book] = {}
        self._members: Dict[str, Member] = {}
        self._checkouts: List[CheckoutRecord] = []

    def get_book(self, isbn: str) -> Optional[Book]:
        return self._books.get(isbn)

    def save_book(self, book: Book) -> None:
        self._books[book.isbn] = book

    def get_member(self, member_id: str) -> Optional[Member]:
        return self._members.get(member_id)

    def save_member(self, member: Member) -> None:
        self._members[member.member_id] = member

    def save_checkout_record(self, record: CheckoutRecord) -> None:
        self._checkouts.append(record)

    def list_books(self) -> List[Book]:
        return list(self._books.values())


# =====================================================================
# LAYER 3 — SERVICE (business logic)
# Depends on domain objects and BookRepository ABC — nothing else.
# =====================================================================
class LibraryService:
    """
    Orchestrates library business workflows.
    Knows nothing about InMemoryBookRepository or any other storage detail.
    """

    def __init__(self, repo: BookRepository):
        if not isinstance(repo, BookRepository):
            raise TypeError("repo must implement BookRepository.")
        self._repo = repo

    def add_book(self, isbn: str, title: str, author: str) -> Book:
        book = Book(isbn=isbn, title=title, author=author)
        self._repo.save_book(book)
        return book

    def register_member(self, member_id: str, name: str) -> Member:
        member = Member(member_id=member_id, name=name)
        self._repo.save_member(member)
        return member

    def checkout_book(self, member_id: str, isbn: str) -> CheckoutRecord:
        """Business workflow: validate → update domain objects → persist → return record."""
        member = self._repo.get_member(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member '{member_id}' not found.")

        book = self._repo.get_book(isbn)
        if book is None:
            raise KeyError(f"Book with ISBN '{isbn}' not found.")

        if not member.can_checkout():
            raise ValueError(f"Member '{member.name}' has reached the 3-book limit.")

        # Domain objects enforce their own rules
        book.mark_checked_out()
        member.checked_out_isbns.append(isbn)

        record = CheckoutRecord(member_id=member_id, isbn=isbn, checkout_date=date.today())

        # Persist updated state
        self._repo.save_book(book)
        self._repo.save_member(member)
        self._repo.save_checkout_record(record)
        return record

    def return_book(self, member_id: str, isbn: str) -> None:
        member = self._repo.get_member(member_id)
        if member is None:
            raise MemberNotFoundError(f"Member '{member_id}' not found.")

        book = self._repo.get_book(isbn)
        if book is None:
            raise KeyError(f"Book with ISBN '{isbn}' not found.")

        book.mark_returned()
        if isbn in member.checked_out_isbns:
            member.checked_out_isbns.remove(isbn)

        self._repo.save_book(book)
        self._repo.save_member(member)

    def list_available_books(self) -> List[Book]:
        return [b for b in self._repo.list_books() if b.available]


# =====================================================================
# DEMONSTRATION
# =====================================================================
if __name__ == "__main__":
    repo = InMemoryBookRepository()
    library = LibraryService(repo=repo)

    # Seed catalogue
    library.add_book("978-0-13-468599-1", "Clean Code",           "Robert C. Martin")
    library.add_book("978-0-20-163361-0", "The Pragmatic Programmer", "Hunt & Thomas")
    library.add_book("978-0-59-651798-1", "Fluent Python",        "Luciano Ramalho")

    # Register member
    gauri = library.register_member("M001", "Gauri Shinde")
    print("Registered:", gauri)

    # Checkout
    rec = library.checkout_book("M001", "978-0-13-468599-1")
    print(f"\nChecked out: due {rec.due_date}")
    print("Available books after checkout:", library.list_available_books())

    # Return
    library.return_book("M001", "978-0-13-468599-1")
    print("\nAfter return, available books:", library.list_available_books())

    # Business rule: 3-book limit
    library.add_book("isbn-4", "Book D", "Author D")
    library.add_book("isbn-5", "Book E", "Author E")
    library.add_book("isbn-6", "Book F", "Author F")
    library.checkout_book("M001", "978-0-20-163361-0")
    library.checkout_book("M001", "978-0-59-51798-1")
    library.checkout_book("M001", "isbn-4")
    try:
        library.checkout_book("M001", "isbn-5")  # should fail
    except ValueError as e:
        print(f"\nLimit enforced: {e}")

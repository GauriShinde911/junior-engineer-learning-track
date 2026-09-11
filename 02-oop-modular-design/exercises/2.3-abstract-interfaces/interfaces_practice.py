"""
Exercise: Interface & Repository Pattern

This exercise demonstrates:
1. Interface Definition (Abstract Base Class `UserRepository`):
   - Defines standard CRUD contract for persistence without exposing storage details.
2. Two distinct implementations of the interface:
   - `InMemoryUserRepository`: Fast in-memory dictionary storage (ideal for unit testing).
   - `JsonFileUserRepository`: File-based persistent storage (JSON on disk).
3. `UserService` (Business Logic Layer):
   - Relies STRICTLY on the `UserRepository` interface (Dependency Inversion Principle).
   - Business rules (e.g. duplicate email checking, status validation) stay 100% agnostic
     of storage mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import json
import os
import tempfile


# =====================================================================
# 1. THE REPOSITORY INTERFACE (CONTRACT)
# =====================================================================
class UserRepository(ABC):
    """
    Abstract interface for User data access.
    Business services depend on this interface, NEVER on concrete databases.
    """

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a user record by unique ID. Returns None if not found."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Fetch a user record by email address."""
        pass

    @abstractmethod
    def save(self, user: Dict[str, Any]) -> None:
        """Create or update a user record."""
        pass

    @abstractmethod
    def list_all(self) -> List[Dict[str, Any]]:
        """List all users in the store."""
        pass


# =====================================================================
# 2. IMPLEMENTATION A: In-Memory Storage (Great for Tests & Mocks)
# =====================================================================
class InMemoryUserRepository(UserRepository):
    """Stores user records in a local Python dictionary."""

    def __init__(self):
        self._storage: Dict[str, Dict[str, Any]] = {}

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        record = self._storage.get(user_id)
        return dict(record) if record else None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        for user in self._storage.values():
            if user.get("email", "").lower() == email.lower():
                return dict(user)
        return None

    def save(self, user: Dict[str, Any]) -> None:
        user_id = user["id"]
        self._storage[user_id] = dict(user)

    def list_all(self) -> List[Dict[str, Any]]:
        return [dict(u) for u in self._storage.values()]


# =====================================================================
# 3. IMPLEMENTATION B: Persistent JSON File Storage
# =====================================================================
class JsonFileUserRepository(UserRepository):
    """Stores and retrieves user records from a JSON file on disk."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            self._write_records({})

    def _read_records(self) -> Dict[str, Dict[str, Any]]:
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _write_records(self, records: Dict[str, Dict[str, Any]]) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def get_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        records = self._read_records()
        record = records.get(user_id)
        return dict(record) if record else None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        records = self._read_records()
        for user in records.values():
            if user.get("email", "").lower() == email.lower():
                return dict(user)
        return None

    def save(self, user: Dict[str, Any]) -> None:
        records = self._read_records()
        records[user["id"]] = user
        self._write_records(records)

    def list_all(self) -> List[Dict[str, Any]]:
        records = self._read_records()
        return list(records.values())


# =====================================================================
# 4. BUSINESS LOGIC: UserService
# Notice: UserService NEVER imports or references InMemory or JsonFile repository!
# =====================================================================
class UserService:
    """
    Core business domain service.
    Directly adheres to Dependency Inversion: depends ONLY on UserRepository (ABC).
    """

    def __init__(self, repository: UserRepository):
        if not isinstance(repository, UserRepository):
            raise TypeError("repository must implement the UserRepository interface")
        self._repository = repository

    def register_user(self, user_id: str, name: str, email: str) -> Dict[str, Any]:
        """Business workflow for registering a user with uniqueness validation."""
        cleaned_email = email.strip().lower()
        if "@" not in cleaned_email:
            raise ValueError(f"Invalid email address: {email}")

        # Business rule: Email must be unique
        if self._repository.get_by_email(cleaned_email) is not None:
            raise ValueError(f"A user with email '{cleaned_email}' already exists.")

        user_data = {
            "id": user_id,
            "name": name.strip(),
            "email": cleaned_email,
            "status": "ACTIVE"
        }
        self._repository.save(user_data)
        return user_data

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Fetch user profile or raise an exception."""
        user = self._repository.get_by_id(user_id)
        if not user:
            raise KeyError(f"User with ID '{user_id}' was not found.")
        return user


# =====================================================================
# DEMONSTRATION & VERIFICATION
# =====================================================================
if __name__ == "__main__":
    print("=" * 65)
    print("DEMO: Running identical business logic against TWO different backends")
    print("=" * 65)

    # 1. Run with InMemoryUserRepository
    print("\n--- 1. Testing with InMemoryUserRepository ---")
    in_memory_repo = InMemoryUserRepository()
    service_mem = UserService(repository=in_memory_repo)
    user1 = service_mem.register_user("U001", "Gauri Shinde", "gauri@example.com")
    print("Registered in memory:", user1)
    print("Fetched profile:", service_mem.get_user_profile("U001"))

    # 2. Run with JsonFileUserRepository
    print("\n--- 2. Testing with JsonFileUserRepository ---")
    temp_json = os.path.join(tempfile.gettempdir(), "demo_users.json")
    try:
        json_repo = JsonFileUserRepository(file_path=temp_json)
        service_file = UserService(repository=json_repo)
        user2 = service_file.register_user("U002", "Alex Mercer", "alex@example.com")
        print(f"Saved to JSON ({temp_json}):", user2)
        print("Fetched from file:", service_file.get_user_profile("U002"))
        print("Total stored in JSON file:", len(json_repo.list_all()))
    finally:
        if os.path.exists(temp_json):
            os.remove(temp_json)

    print("\n[SUCCESS] Business logic operated identically without knowing storage details.")

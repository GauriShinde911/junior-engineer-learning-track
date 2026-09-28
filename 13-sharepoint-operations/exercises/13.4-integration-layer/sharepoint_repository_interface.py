"""
sharepoint_repository_interface.py - Abstract Repository Contract

Defines the interface for persistence operations over SharePoint list items
and documents, decoupling business logic from Microsoft Graph implementation details.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class SharePointRepositoryInterface(ABC):
    """Abstract Base Class specifying data and document persistence contracts."""

    @abstractmethod
    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a domain item by its integer identifier."""
        pass

    @abstractmethod
    def list_items(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query and return domain items matching an optional filter expression."""
        pass

    @abstractmethod
    def save_item(self, data: Dict[str, Any], item_id: Optional[int] = None) -> Dict[str, Any]:
        """Create a new item or update an existing item if item_id is provided."""
        pass

    @abstractmethod
    def delete_item(self, item_id: int) -> bool:
        """Remove a domain item by ID."""
        pass

    @abstractmethod
    def store_document(
        self,
        filename: str,
        content: bytes,
        folder_path: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Upload and store a document file with optional metadata."""
        pass

    @abstractmethod
    def retrieve_document(self, file_path: str) -> bytes:
        """Download binary contents of a stored document."""
        pass

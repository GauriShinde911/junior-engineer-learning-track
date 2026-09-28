"""
service.py - Business Logic Service Layer

Demonstrates Dependency Inversion Principle: AssetService depends strictly
upon the abstract SharePointRepositoryInterface, with zero coupling to HTTP,
Microsoft Graph, or SharePoint API specifics.
"""

from typing import Any, Dict, List, Optional
from sharepoint_repository_interface import SharePointRepositoryInterface


class AssetService:
    """Core domain service for managing hardware assets and operational documents."""

    def __init__(self, repository: SharePointRepositoryInterface):
        # Strict dependency injection against the ABC
        self.repository = repository

    def register_asset(
        self,
        tag: str,
        title: str,
        category: str,
        cost: float,
        manual_bytes: Optional[bytes] = None,
        manual_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register a new asset and optionally archive its technical manual."""
        if not tag.startswith("ENG-HW-"):
            raise ValueError(f"Asset tag '{tag}' does not meet engineering format: ENG-HW-XXXXX")

        if cost < 0:
            raise ValueError("Purchase cost cannot be negative.")

        asset_record = {
            "tag": tag,
            "title": title,
            "category": category,
            "cost": cost,
            "status": "In Service",
        }

        # 1. Persist asset list item via repository interface
        saved_asset = self.repository.save_item(asset_record)

        # 2. If a manual is attached, upload document and link metadata
        if manual_bytes and manual_name:
            doc_meta = {
                "AssetTag": tag,
                "ManualVersion": "1.0.0",
                "Category": category,
            }
            folder = f"Hardware/{category}"
            self.repository.store_document(
                filename=manual_name,
                content=manual_bytes,
                folder_path=folder,
                metadata=doc_meta,
            )
            saved_asset["manual_uploaded"] = True

        return saved_asset

    def get_asset(self, asset_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve an asset by ID."""
        return self.repository.get_item(asset_id)

    def decommission_asset(self, asset_id: int) -> Dict[str, Any]:
        """Update an asset status to Decommissioned."""
        existing = self.repository.get_item(asset_id)
        if not existing:
            raise ValueError(f"Asset #{asset_id} not found.")

        updated_fields = {"status": "Decommissioned"}
        return self.repository.save_item(updated_fields, item_id=asset_id)

    def list_active_laptops(self) -> List[Dict[str, Any]]:
        """Query active laptops."""
        query = "fields/Category eq 'Laptop' and fields/Status eq 'In Service'"
        return self.repository.list_items(filter_query=query)

    def fetch_manual(self, manual_path: str) -> bytes:
        """Download asset documentation."""
        return self.repository.retrieve_document(manual_path)

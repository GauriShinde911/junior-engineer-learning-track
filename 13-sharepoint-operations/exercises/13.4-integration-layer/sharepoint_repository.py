"""
sharepoint_repository.py - Concrete SharePoint Repository Implementation

Implements SharePointRepositoryInterface using SharePointListItemClient,
SharePointDocumentClient, and SharePointFieldMapper.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add sibling directories to path for imports
curr_dir = Path(__file__).resolve().parent
sec2_dir = curr_dir.parent / "13.2-data-operations"
sec3_dir = curr_dir.parent / "13.3-document-operations"
for d in (sec2_dir, sec3_dir):
    if str(d) not in sys.path:
        sys.path.insert(0, str(d))

from field_mapper import SharePointFieldMapper
from list_item_client import (
    SharePointListItemClient,
    SharePointNotFoundError,
)
from document_client import SharePointDocumentClient
from sharepoint_repository_interface import SharePointRepositoryInterface


class SharePointRepository(SharePointRepositoryInterface):
    """Concrete repository executing operations via Graph API clients."""

    def __init__(
        self,
        site_id: str,
        list_id: str,
        drive_id: str,
        mapper: SharePointFieldMapper,
        list_client: SharePointListItemClient,
        doc_client: SharePointDocumentClient,
    ):
        self.site_id = site_id
        self.list_id = list_id
        self.drive_id = drive_id
        self.mapper = mapper
        self.list_client = list_client
        self.doc_client = doc_client

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        try:
            raw = self.list_client.get_item(self.site_id, self.list_id, item_id)
            fields = raw.get("fields", {})
            domain_item = self.mapper.to_python(fields)
            domain_item["id"] = int(raw["id"])
            return domain_item
        except SharePointNotFoundError:
            return None

    def list_items(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        raw_items = self.list_client.list_items(
            self.site_id, self.list_id, filter_query=filter_query
        )
        results = []
        for it in raw_items:
            domain_dict = self.mapper.to_python(it.get("fields", {}))
            domain_dict["id"] = int(it["id"])
            results.append(domain_dict)
        return results

    def save_item(self, data: Dict[str, Any], item_id: Optional[int] = None) -> Dict[str, Any]:
        sp_payload = self.mapper.to_sharepoint(data)
        if item_id:
            raw = self.list_client.update_item(self.site_id, self.list_id, item_id, sp_payload)
            res = self.mapper.to_python(raw)
            res["id"] = item_id
            return res
        else:
            raw = self.list_client.create_item(self.site_id, self.list_id, sp_payload)
            res = self.mapper.to_python(raw.get("fields", {}))
            res["id"] = int(raw.get("id", 0))
            return res

    def delete_item(self, item_id: int) -> bool:
        return self.list_client.delete_item(self.site_id, self.list_id, item_id)

    def store_document(
        self,
        filename: str,
        content: bytes,
        folder_path: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.doc_client.upload_file(
            site_id=self.site_id,
            drive_id=self.drive_id,
            folder_path=folder_path,
            filename=filename,
            content=content,
            metadata=metadata,
        )

    def retrieve_document(self, file_path: str) -> bytes:
        return self.doc_client.download_file(
            site_id=self.site_id, drive_id=self.drive_id, file_path=file_path
        )

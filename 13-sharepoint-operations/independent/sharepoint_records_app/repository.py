"""
repository.py - SharePoint Records App Concrete Repository

Implements CRUD and document operations against the ProjectRecords and
ProjectDeliverables schema specification.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add exercise directories to import clients and field mapper
curr_dir = Path(__file__).resolve().parent
repo_root = curr_dir.parent.parent
sec2_dir = repo_root / "exercises" / "13.2-data-operations"
sec3_dir = repo_root / "exercises" / "13.3-document-operations"
sec4_dir = repo_root / "exercises" / "13.4-integration-layer"
for p in (sec4_dir, sec3_dir, sec2_dir, curr_dir):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
# Ensure curr_dir is strictly first
sys.path.insert(0, str(curr_dir))

from field_mapper import FieldDefinition, SharePointFieldMapper
from list_item_client import SharePointListItemClient, SharePointNotFoundError
from document_client import SharePointDocumentClient
from sharepoint_repository_interface import SharePointRepositoryInterface


# Schema definition matching SCHEMA_SPEC.md
PROJECT_RECORDS_SCHEMA = {
    "title": FieldDefinition("Title", field_type="text", required=True),
    "project_code": FieldDefinition("ProjectCode", field_type="text", required=True),
    "lead_engineer": FieldDefinition("LeadEngineer", field_type="text", required=True),
    "budget": FieldDefinition("Budget", field_type="currency", required=False, default=0.0),
    "phase": FieldDefinition(
        "Phase",
        field_type="choice",
        required=True,
        choices=["Planning", "In Development", "Testing", "Completed", "Archived"],
        default="Planning",
    ),
    "start_date": FieldDefinition("StartDate", field_type="date", required=True),
    "compliance_approved": FieldDefinition(
        "ComplianceApproved", field_type="boolean", required=False, default=False
    ),
}


class ProjectRecordRepository(SharePointRepositoryInterface):
    """Encapsulates data operations for ProjectRecords list and ProjectDeliverables drive."""

    def __init__(
        self,
        site_id: str,
        list_id: str,
        drive_id: str,
        list_client: SharePointListItemClient,
        doc_client: SharePointDocumentClient,
    ):
        self.site_id = site_id
        self.list_id = list_id
        self.drive_id = drive_id
        self.list_client = list_client
        self.doc_client = doc_client
        self.mapper = SharePointFieldMapper(PROJECT_RECORDS_SCHEMA)

    def get_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        try:
            raw = self.list_client.get_item(self.site_id, self.list_id, item_id)
            fields = raw.get("fields", {})
            domain = self.mapper.to_python(fields)
            domain["id"] = int(raw["id"])
            return domain
        except SharePointNotFoundError:
            return None

    def get_by_project_code(self, project_code: str) -> Optional[Dict[str, Any]]:
        """Query single project record by its unique ProjectCode."""
        query = f"fields/ProjectCode eq '{project_code}'"
        items = self.list_items(filter_query=query)
        return items[0] if items else None

    def list_items(self, filter_query: Optional[str] = None) -> List[Dict[str, Any]]:
        raw_items = self.list_client.list_items(
            self.site_id, self.list_id, filter_query=filter_query
        )
        results = []
        for it in raw_items:
            domain = self.mapper.to_python(it.get("fields", {}))
            domain["id"] = int(it.get("id", 0))
            results.append(domain)
        return results

    def save_item(self, data: Dict[str, Any], item_id: Optional[int] = None) -> Dict[str, Any]:
        sp_payload = self.mapper.to_sharepoint(data, partial=bool(item_id))
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

"""
document_client.py - Microsoft Graph Client for SharePoint Document Operations

Handles uploading and downloading binary files, folder hierarchy creation,
and preserving custom metadata fields on SharePoint Document Libraries.
"""

import io
import re
from typing import Any, BinaryIO, Dict, Optional, Union
import requests

from list_item_client import (
    SharePointAuthenticationError,
    SharePointClientError,
    SharePointNotFoundError,
    SharePointThrottledError,
    SharePointValidationError,
)


class SharePointDocumentClient:
    """Manages document library files and folder hierarchies via Microsoft Graph."""

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
    INVALID_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|#%]')

    def __init__(
        self,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        session: Optional[requests.Session] = None,
    ):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = access_token
        self.session = session or requests.Session()

    def get_token(self) -> str:
        """Acquire Bearer token (or return pre-configured test token)."""
        if self._access_token:
            return self._access_token
        raise SharePointAuthenticationError("No token configured or credentials provided.")

    def _headers(self, content_type: str = "application/json") -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": content_type,
            "Accept": "application/json",
        }

    @classmethod
    def sanitize_filename(cls, name: str) -> str:
        """Strip illegal SharePoint characters from filenames."""
        cleaned = cls.INVALID_FILENAME_CHARS.sub("_", name)
        return cleaned.strip(". ")

    def create_folder(self, site_id: str, drive_id: str, parent_path: str, folder_name: str) -> Dict[str, Any]:
        """Create a new folder in a document library drive."""
        clean_name = self.sanitize_filename(folder_name)
        norm_parent = parent_path.strip("/")
        if norm_parent:
            url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/root:/{norm_parent}:/children"
        else:
            url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/root/children"

        payload = {
            "name": clean_name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        resp = self.session.post(url, headers=self._headers(), json=payload)
        return self._handle_response(resp)

    def upload_file(
        self,
        site_id: str,
        drive_id: str,
        folder_path: str,
        filename: str,
        content: Union[bytes, BinaryIO],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Upload file content to SharePoint Document Library.
        If metadata is provided, updates the underlying list item fields in a second step.
        """
        clean_name = self.sanitize_filename(filename)
        norm_path = folder_path.strip("/")
        if norm_path:
            target_url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/root:/{norm_path}/{clean_name}:/content"
        else:
            target_url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/root:/{clean_name}:/content"

        headers = self._headers(content_type="application/octet-stream")
        data = content.read() if hasattr(content, "read") else content

        resp = self.session.put(target_url, headers=headers, data=data)
        item_data = self._handle_response(resp)

        # Update metadata fields on the underlying listItem if specified
        if metadata:
            item_id = item_data.get("id")
            if item_id:
                meta_res = self.update_metadata(site_id, drive_id, item_id, metadata)
                item_data["fields"] = meta_res

        return item_data

    def download_file(self, site_id: str, drive_id: str, file_path: str) -> bytes:
        """Download binary content of a file given its relative path."""
        norm_path = file_path.strip("/")
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/root:/{norm_path}:/content"
        resp = self.session.get(url, headers=self._headers())

        if resp.status_code == 404:
            raise SharePointNotFoundError(f"File '{file_path}' not found on SharePoint drive.")
        elif resp.status_code != 200:
            raise SharePointClientError(f"Download failed with HTTP {resp.status_code}: {resp.text}")

        return resp.content

    def get_metadata(self, site_id: str, drive_id: str, item_id: str) -> Dict[str, Any]:
        """Fetch custom metadata fields for a drive item."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/items/{item_id}/listItem/fields"
        resp = self.session.get(url, headers=self._headers())
        return self._handle_response(resp)

    def update_metadata(
        self, site_id: str, drive_id: str, item_id: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update custom metadata fields on the underlying list item."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/drives/{drive_id}/items/{item_id}/listItem/fields"
        resp = self.session.patch(url, headers=self._headers(), json=metadata)
        return self._handle_response(resp)

    def _handle_response(self, response: requests.Response) -> Any:
        if response.status_code in (200, 201):
            return response.json()
        elif response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise SharePointNotFoundError(f"Resource not found: {response.text}")
        elif response.status_code == 400:
            raise SharePointValidationError(f"Validation failure or bad request: {response.text}")
        elif response.status_code in (401, 403):
            raise SharePointAuthenticationError(f"Unauthorized or Forbidden: {response.text}")
        elif response.status_code == 429:
            retry = int(response.headers.get("Retry-After", 60))
            raise SharePointThrottledError(f"Throttled by Graph API: {response.text}", retry_after=retry)
        else:
            raise SharePointClientError(f"HTTP {response.status_code} Error: {response.text}")

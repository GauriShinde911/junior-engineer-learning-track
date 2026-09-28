"""
list_item_client.py - Microsoft Graph Client for SharePoint List Item Operations

Provides CRUD operations and OData filtering against SharePoint Lists using
Microsoft Graph REST API and MSAL authentication.
"""

from typing import Any, Dict, List, Optional
import requests

try:
    import msal
except ImportError:
    msal = None


class SharePointClientError(Exception):
    """Base exception for SharePoint client errors."""
    pass


class SharePointAuthenticationError(SharePointClientError):
    """Raised when authentication or token acquisition fails."""
    pass


class SharePointNotFoundError(SharePointClientError):
    """Raised when the requested site, list, or item does not exist."""
    pass


class SharePointValidationError(SharePointClientError):
    """Raised when payload fails schema validation or column constraints."""
    pass


class SharePointThrottledError(SharePointClientError):
    """Raised when Microsoft Graph returns 429 Too Many Requests."""

    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after


class SharePointListItemClient:
    """Client for managing SharePoint List Items via Microsoft Graph v1.0."""

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

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
        """Acquire or return cached OAuth2 Bearer token from Azure AD via MSAL."""
        if self._access_token:
            return self._access_token

        if not (self.tenant_id and self.client_id and self.client_secret):
            raise SharePointAuthenticationError(
                "Missing credentials: tenant_id, client_id, and client_secret are required."
            )

        if msal is None:
            raise SharePointAuthenticationError(
                "MSAL library not installed. Cannot perform OAuth2 token exchange."
            )

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret,
        )

        scopes = ["https://graph.microsoft.com/.default"]
        result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            self._access_token = result["access_token"]
            return self._access_token
        else:
            err = result.get("error_description", result.get("error", "Unknown auth failure"))
            raise SharePointAuthenticationError(f"Azure AD Token acquisition failed: {err}")

    def _headers(self) -> Dict[str, str]:
        token = self.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _handle_response(self, response: requests.Response) -> Any:
        if response.status_code in (200, 201):
            return response.json()
        elif response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise SharePointNotFoundError(f"SharePoint resource not found: {response.text}")
        elif response.status_code == 400:
            raise SharePointValidationError(f"Validation failure or bad request: {response.text}")
        elif response.status_code in (401, 403):
            raise SharePointAuthenticationError(f"Unauthorized or Forbidden: {response.text}")
        elif response.status_code == 429:
            retry = int(response.headers.get("Retry-After", 60))
            raise SharePointThrottledError(f"Graph API request throttled: {response.text}", retry_after=retry)
        else:
            raise SharePointClientError(f"HTTP {response.status_code} Error: {response.text}")

    def get_item(self, site_id: str, list_id: str, item_id: int) -> Dict[str, Any]:
        """Fetch a single list item by ID, expanding fields."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items/{item_id}?$expand=fields"
        resp = self.session.get(url, headers=self._headers())
        return self._handle_response(resp)

    def list_items(
        self,
        site_id: str,
        list_id: str,
        filter_query: Optional[str] = None,
        select_fields: Optional[List[str]] = None,
        top: int = 50,
    ) -> List[Dict[str, Any]]:
        """Query items from a list with optional OData $filter and $select."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items"
        params: Dict[str, Any] = {"$expand": "fields", "$top": top}

        if filter_query:
            params["$filter"] = filter_query
        if select_fields:
            params["$select"] = ",".join(select_fields)

        resp = self.session.get(url, headers=self._headers(), params=params)
        data = self._handle_response(resp)
        return data.get("value", [])

    def create_item(self, site_id: str, list_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new list item with the given field attributes."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items"
        payload = {"fields": fields}
        resp = self.session.post(url, headers=self._headers(), json=payload)
        return self._handle_response(resp)

    def update_item(self, site_id: str, list_id: str, item_id: int, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing item fields via PATCH."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items/{item_id}/fields"
        resp = self.session.patch(url, headers=self._headers(), json=fields)
        return self._handle_response(resp)

    def delete_item(self, site_id: str, list_id: str, item_id: int) -> bool:
        """Delete an item by ID."""
        url = f"{self.GRAPH_BASE_URL}/sites/{site_id}/lists/{list_id}/items/{item_id}"
        resp = self.session.delete(url, headers=self._headers())
        return self._handle_response(resp)

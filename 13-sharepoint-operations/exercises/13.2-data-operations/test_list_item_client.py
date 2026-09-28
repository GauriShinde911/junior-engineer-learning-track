"""
test_list_item_client.py - Mocked Unit Tests for SharePoint List Item Operations

Tests CRUD operations, filtering, error handling, and field mapping without
making live network calls to Microsoft Graph.
"""

from datetime import datetime
import pytest
import requests

from field_mapper import FieldDefinition, SharePointFieldMapper
from list_item_client import (
    SharePointAuthenticationError,
    SharePointListItemClient,
    SharePointNotFoundError,
    SharePointThrottledError,
    SharePointValidationError,
)


# ==============================================================================
# FieldMapper Tests
# ==============================================================================

@pytest.fixture
def asset_mapper():
    schema = {
        "title": FieldDefinition("Title", field_type="text", required=True),
        "tag": FieldDefinition("AssetTag", field_type="text", required=True),
        "category": FieldDefinition(
            "Category",
            field_type="choice",
            required=True,
            choices=["Laptop", "Workstation", "Server"],
        ),
        "cost": FieldDefinition("PurchaseCost", field_type="currency", required=False),
        "in_service": FieldDefinition("InService", field_type="boolean", default=True),
        "purchased_at": FieldDefinition("PurchaseDate", field_type="date", required=False),
    }
    return SharePointFieldMapper(schema)


def test_field_mapper_to_sharepoint_success(asset_mapper):
    data = {
        "title": "MacBook Pro 16",
        "tag": "ENG-HW-00101",
        "category": "Laptop",
        "cost": 2499.50,
        "in_service": True,
        "purchased_at": datetime(2026, 1, 15),
    }
    sp_payload = asset_mapper.to_sharepoint(data)

    assert sp_payload["Title"] == "MacBook Pro 16"
    assert sp_payload["AssetTag"] == "ENG-HW-00101"
    assert sp_payload["Category"] == "Laptop"
    assert sp_payload["PurchaseCost"] == 2499.50
    assert sp_payload["InService"] is True
    assert sp_payload["PurchaseDate"] == "2026-01-15T00:00:00Z"


def test_field_mapper_missing_required_field_raises_error(asset_mapper):
    invalid_data = {
        "title": "MacBook Pro 16",
        # missing "tag"
        "category": "Laptop",
    }
    with pytest.raises(ValueError, match="Required field 'tag' is missing"):
        asset_mapper.to_sharepoint(invalid_data)


def test_field_mapper_invalid_choice_raises_error(asset_mapper):
    invalid_data = {
        "title": "Main Router",
        "tag": "ENG-HW-00999",
        "category": "Networking",  # Not in allowed choices
    }
    with pytest.raises(ValueError, match="not in allowed choices"):
        asset_mapper.to_sharepoint(invalid_data)


def test_field_mapper_to_python(asset_mapper):
    sp_data = {
        "Title": "Dell Precision",
        "AssetTag": "ENG-HW-00202",
        "Category": "Workstation",
        "PurchaseCost": 3100.0,
        "InService": False,
        "PurchaseDate": "2026-03-20T00:00:00Z",
    }
    py_data = asset_mapper.to_python(sp_data)

    assert py_data["title"] == "Dell Precision"
    assert py_data["tag"] == "ENG-HW-00202"
    assert py_data["cost"] == 3100.0
    assert py_data["in_service"] is False
    assert isinstance(py_data["purchased_at"], datetime)


# ==============================================================================
# SharePointListItemClient Mocked HTTP Tests
# ==============================================================================

@pytest.fixture
def mock_client():
    return SharePointListItemClient(access_token="fake-test-token-xyz")


def test_get_item_success(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "id": "42",
        "fields": {"Title": "MacBook Pro", "AssetTag": "ENG-HW-001"},
    }
    mocker.patch.object(mock_client.session, "get", return_value=fake_response)

    item = mock_client.get_item(site_id="site-123", list_id="list-456", item_id=42)

    assert item["id"] == "42"
    assert item["fields"]["AssetTag"] == "ENG-HW-001"


def test_get_item_not_found(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 404
    fake_response.text = "Item does not exist."
    mocker.patch.object(mock_client.session, "get", return_value=fake_response)

    with pytest.raises(SharePointNotFoundError):
        mock_client.get_item(site_id="site-123", list_id="list-456", item_id=999)


def test_create_item_success(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 201
    fake_response.json.return_value = {
        "id": "101",
        "fields": {"Title": "Dell Server", "AssetTag": "ENG-HW-003"},
    }
    mocker.patch.object(mock_client.session, "post", return_value=fake_response)

    payload = {"Title": "Dell Server", "AssetTag": "ENG-HW-003"}
    res = mock_client.create_item(site_id="site-123", list_id="list-456", fields=payload)

    assert res["id"] == "101"
    assert res["fields"]["Title"] == "Dell Server"


def test_create_item_validation_failure(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 400
    fake_response.text = "One or more column values are invalid."
    mocker.patch.object(mock_client.session, "post", return_value=fake_response)

    with pytest.raises(SharePointValidationError):
        mock_client.create_item(site_id="site-123", list_id="list-456", fields={})


def test_list_items_with_filter(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "value": [
            {"id": "1", "fields": {"AssetTag": "ENG-HW-001"}},
            {"id": "2", "fields": {"AssetTag": "ENG-HW-002"}},
        ]
    }
    mock_get = mocker.patch.object(mock_client.session, "get", return_value=fake_response)

    filter_expr = "fields/Category eq 'Laptop'"
    items = mock_client.list_items(site_id="site-123", list_id="list-456", filter_query=filter_expr)

    assert len(items) == 2
    mock_get.assert_called_once()
    assert mock_get.call_args[1]["params"]["$filter"] == filter_expr


def test_update_item_success(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 200
    fake_response.json.return_value = {"Status": "In Maintenance"}
    mocker.patch.object(mock_client.session, "patch", return_value=fake_response)

    res = mock_client.update_item("site-1", "list-1", 10, {"Status": "In Maintenance"})
    assert res["Status"] == "In Maintenance"


def test_delete_item_success(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 204
    mocker.patch.object(mock_client.session, "delete", return_value=fake_response)

    res = mock_client.delete_item("site-1", "list-1", 10)
    assert res is True


def test_throttling_raises_throttled_error(mock_client, mocker):
    fake_response = mocker.Mock(spec=requests.Response)
    fake_response.status_code = 429
    fake_response.headers = {"Retry-After": "120"}
    fake_response.text = "Too Many Requests"
    mocker.patch.object(mock_client.session, "get", return_value=fake_response)

    with pytest.raises(SharePointThrottledError) as exc_info:
        mock_client.get_item("site-1", "list-1", 1)
    assert exc_info.value.retry_after == 120


def test_missing_credentials_raises_auth_error():
    client = SharePointListItemClient()
    with pytest.raises(SharePointAuthenticationError, match="Missing credentials"):
        client.get_token()

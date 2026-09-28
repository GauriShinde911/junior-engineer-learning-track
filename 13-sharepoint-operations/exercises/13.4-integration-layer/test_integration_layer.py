"""
test_integration_layer.py - Unit Tests for Repository and Service Abstraction

Verifies that AssetService coordinates operations through the abstract
repository interface with zero direct coupling to SharePoint or Graph API.
"""

import sys
from pathlib import Path
import pytest
from unittest.mock import Mock

curr_dir = Path(__file__).resolve().parent
if str(curr_dir) not in sys.path:
    sys.path.insert(0, str(curr_dir))

if "service" in sys.modules and not hasattr(sys.modules["service"], "AssetService"):
    del sys.modules["service"]

from sharepoint_repository_interface import SharePointRepositoryInterface
from service import AssetService


@pytest.fixture
def mock_repo():
    repo = Mock(spec=SharePointRepositoryInterface)
    return repo


@pytest.fixture
def asset_service(mock_repo):
    return AssetService(repository=mock_repo)


def test_register_asset_success_without_manual(asset_service, mock_repo):
    mock_repo.save_item.return_value = {
        "id": 1,
        "tag": "ENG-HW-00101",
        "title": "MacBook Pro 16",
        "category": "Laptop",
        "cost": 2499.0,
        "status": "In Service",
    }

    result = asset_service.register_asset(
        tag="ENG-HW-00101",
        title="MacBook Pro 16",
        category="Laptop",
        cost=2499.0,
    )

    assert result["id"] == 1
    assert result["tag"] == "ENG-HW-00101"
    mock_repo.save_item.assert_called_once()
    mock_repo.store_document.assert_not_called()


def test_register_asset_with_manual_upload(asset_service, mock_repo):
    mock_repo.save_item.return_value = {
        "id": 2,
        "tag": "ENG-HW-00202",
        "title": "Dell Workstation",
        "category": "Workstation",
        "cost": 3200.0,
        "status": "In Service",
    }
    mock_repo.store_document.return_value = {"id": "doc-55"}

    result = asset_service.register_asset(
        tag="ENG-HW-00202",
        title="Dell Workstation",
        category="Workstation",
        cost=3200.0,
        manual_bytes=b"%PDF-sample",
        manual_name="dell_precision_spec.pdf",
    )

    assert result["id"] == 2
    assert result["manual_uploaded"] is True
    mock_repo.store_document.assert_called_once_with(
        filename="dell_precision_spec.pdf",
        content=b"%PDF-sample",
        folder_path="Hardware/Workstation",
        metadata={
            "AssetTag": "ENG-HW-00202",
            "ManualVersion": "1.0.0",
            "Category": "Workstation",
        },
    )


def test_register_asset_invalid_tag_raises_error(asset_service):
    with pytest.raises(ValueError, match="does not meet engineering format"):
        asset_service.register_asset(
            tag="INVALID-TAG-123",
            title="Old Monitor",
            category="Peripherals",
            cost=150.0,
        )


def test_register_asset_negative_cost_raises_error(asset_service):
    with pytest.raises(ValueError, match="Purchase cost cannot be negative"):
        asset_service.register_asset(
            tag="ENG-HW-00303",
            title="Keyboard",
            category="Peripherals",
            cost=-50.0,
        )


def test_decommission_asset(asset_service, mock_repo):
    mock_repo.get_item.return_value = {"id": 1, "status": "In Service"}
    mock_repo.save_item.return_value = {"id": 1, "status": "Decommissioned"}

    res = asset_service.decommission_asset(asset_id=1)

    assert res["status"] == "Decommissioned"
    mock_repo.save_item.assert_called_once_with({"status": "Decommissioned"}, item_id=1)


def test_decommission_asset_not_found_raises_error(asset_service, mock_repo):
    mock_repo.get_item.return_value = None

    with pytest.raises(ValueError, match="Asset #999 not found"):
        asset_service.decommission_asset(asset_id=999)

"""
test_repository_mocked.py - Mocked Unit Tests for Project Records App

Tests end-to-end CRUD operations, document deliverable storage, and business rule
enforcement using mocked HTTP responses and mock clients.
"""

import sys
from pathlib import Path
from unittest.mock import Mock
import pytest

curr_dir = Path(__file__).resolve().parent
if str(curr_dir) not in sys.path:
    sys.path.insert(0, str(curr_dir))

if "service" in sys.modules and not hasattr(sys.modules["service"], "ProjectRecordsService"):
    del sys.modules["service"]

from repository import ProjectRecordRepository
from service import ProjectRecordsService
from list_item_client import SharePointListItemClient
from document_client import SharePointDocumentClient


@pytest.fixture
def mock_list_client():
    return Mock(spec=SharePointListItemClient)


@pytest.fixture
def mock_doc_client():
    return Mock(spec=SharePointDocumentClient)


@pytest.fixture
def repo(mock_list_client, mock_doc_client):
    return ProjectRecordRepository(
        site_id="eng-site-id",
        list_id="proj-list-id",
        drive_id="deliv-drive-id",
        list_client=mock_list_client,
        doc_client=mock_doc_client,
    )


@pytest.fixture
def project_service(repo):
    return ProjectRecordsService(repository=repo)


def test_create_project_success(project_service, mock_list_client):
    # No existing project with this code
    mock_list_client.list_items.return_value = []
    mock_list_client.create_item.return_value = {
        "id": "10",
        "fields": {
            "Title": "Autonomous Robotics Core",
            "ProjectCode": "PRJ-1044",
            "LeadEngineer": "lead@company.com",
            "Budget": 50000.0,
            "Phase": "Planning",
            "StartDate": "2026-10-01",
            "ComplianceApproved": False,
        },
    }

    result = project_service.create_project(
        project_code="PRJ-1044",
        title="Autonomous Robotics Core",
        lead_engineer="lead@company.com",
        start_date="2026-10-01",
        budget=50000.0,
    )

    assert result["id"] == 10
    assert result["project_code"] == "PRJ-1044"
    assert result["phase"] == "Planning"
    assert result["compliance_approved"] is False


def test_create_project_invalid_code_format(project_service):
    with pytest.raises(ValueError, match="Invalid project code format"):
        project_service.create_project(
            project_code="INVALID_CODE",
            title="Bad Code Project",
            lead_engineer="dev@company.com",
            start_date="2026-10-01",
        )


def test_create_project_duplicate_code_rejected(project_service, mock_list_client):
    mock_list_client.list_items.return_value = [
        {"id": "5", "fields": {"ProjectCode": "PRJ-2020", "Title": "Existing"}}
    ]

    with pytest.raises(ValueError, match="already exists"):
        project_service.create_project(
            project_code="PRJ-2020",
            title="Duplicate Code Project",
            lead_engineer="dev@company.com",
            start_date="2026-10-01",
        )


def test_upload_deliverable_success(project_service, mock_list_client, mock_doc_client):
    # Project exists
    mock_list_client.list_items.return_value = [
        {"id": "10", "fields": {"ProjectCode": "PRJ-1044", "Title": "Robotics Core"}}
    ]
    mock_doc_client.upload_file.return_value = {
        "id": "doc-901",
        "name": "arch_spec.pdf",
        "fields": {
            "ProjectCode": "PRJ-1044",
            "DocCategory": "DesignSpec",
            "SignoffStatus": "Pending",
        },
    }

    res = project_service.upload_deliverable(
        project_code="PRJ-1044",
        filename="arch_spec.pdf",
        content=b"%PDF-spec-bytes",
        category="DesignSpec",
    )

    assert res["id"] == "doc-901"
    mock_doc_client.upload_file.assert_called_once_with(
        site_id="eng-site-id",
        drive_id="deliv-drive-id",
        folder_path="PRJ-1044/designspecs",
        filename="arch_spec.pdf",
        content=b"%PDF-spec-bytes",
        metadata={
            "ProjectCode": "PRJ-1044",
            "DocCategory": "DesignSpec",
            "SignoffStatus": "Pending",
        },
    )


def test_upload_deliverable_invalid_category(project_service):
    with pytest.raises(ValueError, match="Invalid document category"):
        project_service.upload_deliverable(
            project_code="PRJ-1044",
            filename="doc.pdf",
            content=b"bytes",
            category="NonExistentCategory",
        )


def test_advance_phase_without_compliance_rejected(project_service, mock_list_client):
    mock_list_client.list_items.return_value = [
        {
            "id": "10",
            "fields": {
                "ProjectCode": "PRJ-1044",
                "Phase": "Testing",
                "ComplianceApproved": False,
            },
        }
    ]

    with pytest.raises(ValueError, match="lacks compliance approval"):
        project_service.advance_phase("PRJ-1044", "Completed")


def test_advance_phase_with_compliance_succeeds(project_service, mock_list_client):
    mock_list_client.list_items.return_value = [
        {
            "id": "10",
            "fields": {
                "ProjectCode": "PRJ-1044",
                "Phase": "Testing",
                "ComplianceApproved": True,
            },
        }
    ]
    mock_list_client.update_item.return_value = {
        "Phase": "Completed",
        "ComplianceApproved": True,
    }

    res = project_service.advance_phase("PRJ-1044", "Completed")
    assert res["phase"] == "Completed"

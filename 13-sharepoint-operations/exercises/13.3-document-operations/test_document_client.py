"""
test_document_client.py - Mocked Unit Tests for SharePoint Document Operations

Tests uploading, downloading, folder organization, metadata preservation,
and missing file handling via Microsoft Graph API without making live calls.
"""

import sys
from pathlib import Path
import pytest
import requests

# Ensure 13.2 directory is importable for shared client exceptions if needed
curr_dir = Path(__file__).resolve().parent
sec2_dir = curr_dir.parent / "13.2-data-operations"
if str(sec2_dir) not in sys.path:
    sys.path.insert(0, str(sec2_dir))

from document_client import (
    SharePointDocumentClient,
    SharePointNotFoundError,
    SharePointValidationError,
)


@pytest.fixture
def doc_client():
    return SharePointDocumentClient(access_token="fake-doc-token-abc")


def test_sanitize_filename():
    unsafe = 'Report: Q3/2026*final?.pdf'
    safe = SharePointDocumentClient.sanitize_filename(unsafe)
    assert safe == "Report_ Q3_2026_final_.pdf"
    assert ":" not in safe
    assert "/" not in safe
    assert "*" not in safe


def test_upload_file_success_without_metadata(doc_client, mocker):
    fake_put = mocker.Mock(spec=requests.Response)
    fake_put.status_code = 201
    fake_put.json.return_value = {
        "id": "item-999",
        "name": "manual.pdf",
        "size": 1024,
    }
    mocker.patch.object(doc_client.session, "put", return_value=fake_put)

    res = doc_client.upload_file(
        site_id="site-1",
        drive_id="drive-1",
        folder_path="Hardware/Manuals",
        filename="manual.pdf",
        content=b"Sample PDF bytes",
    )

    assert res["id"] == "item-999"
    assert res["name"] == "manual.pdf"


def test_upload_file_preserves_metadata(doc_client, mocker):
    # Phase 1: file upload PUT returns driveItem
    fake_put = mocker.Mock(spec=requests.Response)
    fake_put.status_code = 201
    fake_put.json.return_value = {"id": "item-999", "name": "specs.pdf"}
    mocker.patch.object(doc_client.session, "put", return_value=fake_put)

    # Phase 2: metadata PATCH returns updated fields
    fake_patch = mocker.Mock(spec=requests.Response)
    fake_patch.status_code = 200
    fake_patch.json.return_value = {
        "ManualVersion": "1.0.0",
        "Manufacturer": "Dell",
    }
    mocker.patch.object(doc_client.session, "patch", return_value=fake_patch)

    metadata = {"ManualVersion": "1.0.0", "Manufacturer": "Dell"}
    res = doc_client.upload_file(
        site_id="site-1",
        drive_id="drive-1",
        folder_path="Hardware/Dell",
        filename="specs.pdf",
        content=b"Specs binary data",
        metadata=metadata,
    )

    assert res["id"] == "item-999"
    assert res["fields"]["ManualVersion"] == "1.0.0"
    assert res["fields"]["Manufacturer"] == "Dell"


def test_download_file_success(doc_client, mocker):
    fake_get = mocker.Mock(spec=requests.Response)
    fake_get.status_code = 200
    fake_get.content = b"%PDF-1.4 file binary content"
    mocker.patch.object(doc_client.session, "get", return_value=fake_get)

    data = doc_client.download_file(
        site_id="site-1",
        drive_id="drive-1",
        file_path="Hardware/Dell/specs.pdf",
    )

    assert data == b"%PDF-1.4 file binary content"


def test_download_file_missing_handled(doc_client, mocker):
    fake_get = mocker.Mock(spec=requests.Response)
    fake_get.status_code = 404
    fake_get.text = "The resource could not be found."
    mocker.patch.object(doc_client.session, "get", return_value=fake_get)

    with pytest.raises(SharePointNotFoundError, match="File 'Hardware/missing.pdf' not found"):
        doc_client.download_file(
            site_id="site-1",
            drive_id="drive-1",
            file_path="Hardware/missing.pdf",
        )


def test_create_folder(doc_client, mocker):
    fake_post = mocker.Mock(spec=requests.Response)
    fake_post.status_code = 201
    fake_post.json.return_value = {"id": "folder-123", "name": "Apple"}
    mocker.patch.object(doc_client.session, "post", return_value=fake_post)

    folder = doc_client.create_folder(
        site_id="site-1",
        drive_id="drive-1",
        parent_path="Hardware",
        folder_name="Apple",
    )

    assert folder["id"] == "folder-123"
    assert folder["name"] == "Apple"

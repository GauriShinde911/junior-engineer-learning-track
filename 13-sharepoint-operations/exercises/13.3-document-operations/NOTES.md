# 13.3 SharePoint Document Operations

## Core Concept
Document operations manage binary files, directory hierarchies, and document-level custom metadata within SharePoint Document Libraries. Unlike raw blob storage (such as AWS S3 or Azure Blob), SharePoint couples binary content with structured list-item columns, version histories, and folder containment.

## Key Tools and Graph API Concepts
- **Drive (`/drives/{drive-id}`)**: Represents a SharePoint Document Library as a storage volume in Microsoft Graph.
- **DriveItem (`/items/{item-id}`)**: An addressable file or folder within a drive, containing file system attributes (size, mimeType, eTag, cTag).
- **`...:/content` Endpoint**: Direct binary stream endpoint used with `PUT` (for small uploads < 4MB) or `GET` (for downloads).
- **`listItem/fields` Endpoint**: The sub-resource on a DriveItem where custom business metadata columns are stored and updated.

## Practical Theory: The Two-Phase Upload Pattern
A common bug in SharePoint integrations is uploading a file and expecting custom column values to appear immediately. In Microsoft Graph, uploading via `PUT /content` creates the binary `DriveItem` resource. However, custom metadata columns belong to the underlying SharePoint list item that backs the file. Therefore, creating a complete document record is a **two-phase operation**:
1. Upload the raw byte stream to initialize or replace the file binary.
2. Send a `PATCH` request to `items/{item-id}/listItem/fields` with the typed metadata payload.

## Connection to What Was Built
This folder implements `document_client.py`, which provides binary upload/download, folder creation, filename sanitization, and the two-phase metadata preservation flow. `test_document_client.py` uses mocked HTTP responses to verify file uploads, metadata retention, folder creation, and missing file error handling.

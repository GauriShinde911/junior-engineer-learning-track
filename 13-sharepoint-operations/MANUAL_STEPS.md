# Manual Steps: Validating Against a Live SharePoint Site

> **Reality Check**: Live SharePoint list CRUD and document operations require an active Microsoft 365 tenant, an Azure App Registration, and a provisioned SharePoint site collection. These cannot be validated in automated CI without live credentials. Follow these steps to validate your implementation against a real environment.

---

## 1. Prerequisites in Microsoft Entra ID (Azure AD)

1. **Create an App Registration**:
   - Navigate to **Microsoft Entra admin center** -> **App registrations** -> **New registration**.
   - Name: `JuniorTrack-SharePoint-Operations`.
   - Supported account types: Single tenant.
2. **Generate Client Secret**:
   - Go to **Certificates & secrets** -> **New client secret**.
   - Note the secret value immediately.
3. **Configure API Permissions (Least Privilege)**:
   - Select **API permissions** -> **Add a permission** -> **Microsoft Graph** -> **Application permissions**.
   - Add `Sites.Selected` (or `Sites.ReadWrite.All` if testing in a disposable developer sandbox).
   - Click **Grant admin consent for <Tenant>**.

---

## 2. Setting Up the Target SharePoint Site

1. In SharePoint admin center, create a private Team Site using the specification in `exercises/13.1-concepts/TRAINING_SITE_SPEC.md`.
2. Retrieve the `Site ID` using Graph Explorer:
   ```http
   GET https://graph.microsoft.com/v1.0/sites/<tenant>.sharepoint.com:/sites/EngOpsHub
   ```
3. Create the `HardwareAssets` list and `EngineeringManuals` document library.

---

## 3. Configuring Local Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp 13-sharepoint-operations/.env.example 13-sharepoint-operations/.env
   ```
2. Populate `.env` with your real tenant ID, client ID, client secret, and target IDs.
3. Run the live verification script (or load `.env` with `python-dotenv`):
   ```python
   import os
   from dotenv import load_dotenv
   from exercises.13_2_data_operations.list_item_client import SharePointListItemClient

   load_dotenv("13-sharepoint-operations/.env")
   client = SharePointListItemClient(
       tenant_id=os.getenv("SHAREPOINT_TENANT_ID"),
       client_id=os.getenv("SHAREPOINT_CLIENT_ID"),
       client_secret=os.getenv("SHAREPOINT_CLIENT_SECRET"),
   )
   token = client.get_token()
   print("Successfully authenticated with Azure AD! Token acquired.")
   ```

---

## 4. Verification Checklist

- [ ] Token acquisition returns a valid JWT without 401 Unauthorized errors.
- [ ] Creating an item via `list_item_client.create_item()` creates a visible row in the SharePoint List UI.
- [ ] Updating the item status modifies the row without duplicating records.
- [ ] Uploading a file via `document_client.upload_file()` creates the file and sets custom metadata columns visible in Document Library view.
- [ ] Downloading the file retrieves identical binary bytes (verifiable via SHA256 checksum).
- [ ] Deleting the test item moves it to the site recycle bin.

# SharePoint & Graph API Troubleshooting Notes

A diagnostic field guide for distinguishing permissions, throttling, and connectivity errors when integrating applications with Microsoft Graph and SharePoint.

---

## 1. Quick Diagnostic Triage Matrix

| Observed Error | Layer | Cause | Initial Diagnostic Check |
|---|---|---|---|
| **`403 Forbidden` / `AccessDenied`** | Authorization | App registration lacks required Graph scopes, admin consent was not granted, or app lacks role assignment on site. | Inspect Azure Portal App Registration API permissions and site-level permissions via `Sites.Selected`. |
| **`429 Too Many Requests`** | Capacity / Rate Limit | Application exceeded Graph API per-app/per-tenant burst or concurrency thresholds. | Check `Retry-After` HTTP response header and inspect request burst frequency. |
| **`ConnectionError` / `Timeout`** | Transport / Network | DNS lookup failed, corporate proxy/firewall blocked outbound port 443, or network interface down. | Test connectivity to `https://login.microsoftonline.com` and `https://graph.microsoft.com` via `curl` / `nc`. |

---

## 2. Detailed Failure Scenarios & Troubleshooting

### Scenario 1: HTTP 403 Forbidden / `AccessDenied`
- **How to identify**: HTTP status 403 returned with response body containing `{"error": {"code": "AccessDenied", ...}}` or `"InsufficientPrivileges"`.
- **Key distinction**: Network connectivity and token acquisition succeeded! The token was presented, but Azure AD or SharePoint determined the caller lacks rights to the target container.
- **What to check first**:
  1. **Application vs Delegated Scopes**: Did you grant `Application` permissions (for daemon/backend services using client credentials) rather than `Delegated` permissions (which require an interactive user)?
  2. **Admin Consent**: In Azure Portal (`App Registrations -> API Permissions`), check if the status indicator shows a green checkmark (`Granted for <Tenant>`). Unconsented permissions result in immediate 403s.
  3. **`Sites.Selected` Scoping**: If using least-privilege `Sites.Selected`, confirm an administrator explicitly assigned permissions to your application ID on that specific site collection via POST to `https://graph.microsoft.com/v1.0/sites/{site-id}/permissions`.

---

### Scenario 2: HTTP 429 Too Many Requests (Throttling)
- **How to identify**: HTTP status 429 returned with error code `activityLimitReached` or `ApplicationThrottled`. The response headers will include `Retry-After: <seconds>`.
- **Key distinction**: The request was completely valid and authorized, but the tenant-wide or application rate-limit bucket has been exhausted.
- **What to check first**:
  1. **Read `Retry-After` Header**: Never retry immediately in a tight loop. Extract `int(response.headers.get("Retry-After", 60))` and sleep for that duration.
  2. **Implement Exponential Backoff with Jitter**: Wrap Graph API calls with retry logic:
     $$\text{delay} = \min(\text{cap}, \text{base} \times 2^{\text{attempt}}) + \text{random\_jitter}$$
  3. **Batching & Paging**: Are you querying all items without `$top` or firing unbounded parallel threads? Reduce page sizes to 50–100 items.

---

### Scenario 3: Network Connection / Timeout Failures
- **How to identify**: No HTTP status code is received. Python raises `requests.exceptions.ConnectionError` or `requests.exceptions.Timeout`.
- **Key distinction**: The request never reached Microsoft's servers. There is no Azure AD token verification or SharePoint evaluation.
- **What to check first**:
  1. **Verify Outbound TLS 443**: Ensure host can reach Microsoft login and Graph domains:
     ```bash
     curl -v https://login.microsoftonline.com/healthz
     curl -v https://graph.microsoft.com/v1.0/$metadata
     ```
  2. **Corporate Proxy / SSL Inspection**: If corporate proxies intercept HTTPS, ensure the proxy CA bundle is trusted in Python (`REQUESTS_CA_BUNDLE` environment variable).
  3. **DNS Resolution**: Confirm `graph.microsoft.com` resolves to valid Microsoft IPs from the deployment host.

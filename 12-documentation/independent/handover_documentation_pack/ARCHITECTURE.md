# Architecture Document: Local Secret Vault (`undocumented_app`)

This document describes the architectural layout, data structures, encryption model, and trade-offs of the `undocumented_app` (Vault CLI).

---

## 1. System Overview & Component Diagram

The Vault CLI is a lightweight, single-process, file-backed key-value store with integrated symmetric ciphering and TTL expiration.

```text
       ┌────────────────────────────────────────────────────────┐
       │                      CLI Interface                     │
       │           (argparse subcommands: set, get, ...)        │
       └───────────────────────────┬────────────────────────────┘
                                   │
                   Calls storage & lifecycle functions
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          Vault Core Engine                             │
│   • Key derivation: SHA-256(VAULT_SECRET_KEY)                          │
│   • Stream XOR obfuscator / de-obfuscator (_enc, _dec)                │
│   • Serialization: JSON encoder / decoder                             │
│   • Lifecycle & TTL evaluator: (time.time() > item.expires)           │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                    Writes / reads base64 stream
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         Persistent Disk File                          │
│      vault.dat (or $VAULT_STORAGE_PATH) — Base64 XOR Ciphertext        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. In-Memory Data Model

When decrypted into memory, the vault state is a Python dictionary where keys map to structured secret objects:

```json
{
  "DB_PASSWORD": {
    "val": "SecretPass123!",
    "created": "2026-09-26T14:10:00Z",
    "expires": 0,
    "rev": 1
  },
  "TEMP_TOKEN": {
    "val": "tok_xyz999",
    "created": "2026-09-26T14:12:00Z",
    "expires": 1790431920,
    "rev": 2
  }
}
```

### Schema Attributes
| Attribute | Type | Description |
|---|---|---|
| `val` | String | Plaintext secret value. |
| `created` | String (ISO 8601) | UTC timestamp of initial storage or last update. |
| `expires` | Integer (Unix Epoch) | Expiration timestamp in seconds. `0` indicates no expiration. |
| `rev` | Integer | Monotonically increasing revision counter incremented on every `set`. |

---

## 3. Cryptographic & Data Transformation Flow

### Write Flow (`set` / `purge`)
1. User supplies secret string via CLI argument.
2. `_k()` computes a 32-byte SHA-256 digest of the master secret key `VAULT_SECRET_KEY`.
3. The in-memory dictionary is serialized to a UTF-8 JSON byte string.
4. `_enc()` applies a repeating-key XOR operation between the JSON byte array and the 32-byte key digest.
5. The resulting ciphertext is Base64-encoded to prevent encoding corruption and written to `vault.dat`.

### Read Flow (`get` / `audit`)
1. File is read from disk.
2. `_dec()` decodes Base64 into raw ciphertext bytes, reapplies XOR with SHA-256 digest (symmetric inverse), and reconstructs UTF-8 JSON.
3. If an accessed key has `expires > 0` and `current_epoch > expires`, the key is immediately purged and omitted from the return payload.

---

## 4. Key Architectural Decisions & Rationale

### Decision 1: Pure Standard Library vs External Cryptography
- **Context**: The application required local secret obfuscation without requiring external C extensions or wheels (such as `cryptography` / OpenSSL).
- **Decision**: Implemented SHA-256 key stretching paired with a repeating-key XOR stream transform using standard `hashlib` and `base64`.
- **Trade-off**: Maintains 100% standard library compatibility and zero installation overhead across any Python environment. However, XOR ciphers are susceptible to known-plaintext analysis; this design is suitable for local development secret protection, but not for high-threat multi-tenant cloud security.

### Decision 2: Lazy vs Eager Expiration
- **Context**: Expired keys could be purged via a continuous daemon or upon access.
- **Decision**: Implemented lazy on-demand expiration during `get` calls, complemented by an explicit `purge` CLI command.
- **Trade-off**: Requires zero background daemon threads or cron dependencies while keeping storage tidy through routine operations.

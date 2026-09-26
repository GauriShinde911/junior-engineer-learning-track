# Changelog: DataFlow Sync Engine

All notable changes to the DataFlow Sync Engine will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-09-15

### User Impact Summary
Version 2.0.0 represents a major architectural upgrade that migrates database synchronization from polling to real-time Change Data Capture (CDC). This provides near-instantaneous data sync (<2 seconds vs 60 seconds) and eliminates high CPU polling overhead. **Breaking Change**: Legacy YAML configuration formats and deprecated v1 REST endpoints have been retired. All consumers must migrate to JSON/env configs and API v2.

### Added
- Real-time PostgreSQL CDC streaming via logical replication slots (`wal2json`).
- Prometheus metrics endpoint at `/metrics` exporting sync latency and throughput counters.
- Built-in AES-256 encryption at rest for intermediate local spool buffers.

### Changed
- **BREAKING**: Configuration engine now expects JSON format or environment variables; `.sync-config.yaml` is no longer parsed.
- **BREAKING**: The webhook callback payload schema now wraps events in an `events` array rather than emitting root objects.
- Minimum supported Python runtime raised from 3.8 to 3.11.

### Removed
- **BREAKING**: Removed polling-based sync worker (`workers/poller.py`).
- **BREAKING**: Removed legacy `/api/v1/sync/trigger` endpoint in favor of `/api/v2/pipelines/{id}/sync`.

### Fixed
- Fixed memory accumulation bug where unacknowledged batch buffers leaked during network partitions (#184).
- Resolved deadlock issue occurring when concurrent pipeline definitions referenced the same target table (#192).

### Security
- Updated dependency `cryptography` to `>=43.0.0` to resolve CVE-2024-XXXX (timing side-channel vulnerability in key derivation).

### Migration Notes (Breaking Changes)
1. **Config Migration**:
   Convert existing YAML files to JSON using the migration script:
   ```bash
   python -m scripts.migrate_config_v1_to_v2 --input config.yaml --output config.json
   ```
2. **Replication Permissions**:
   The PostgreSQL user account requires `REPLICATION` privileges in Postgres:
   ```sql
   ALTER USER dataflow_sync WITH REPLICATION;
   ```
3. **API Consumer Updates**:
   Update webhook receivers to inspect `payload["events"]` instead of top-level event fields.

### Known Issues
- CDC stream initialization may take up to 45 seconds when establishing replication slots on databases with very large initial WAL backlogs (>10GB).
- Windows installations require manual creation of `%LOCALAPPDATA%\DataFlow\spool` if run under non-interactive service accounts.

---

## [1.1.0] - 2026-05-20

### User Impact Summary
This release introduces automated CSV and Parquet export capabilities and improves sync resilience over flaky networks with automatic retry backoff. Existing workflows and configuration files remain 100% backward compatible.

### Added
- Export support for Apache Parquet and compressed CSV output sinks.
- Configurable exponential backoff retry mechanism for transient target database disconnects (`retry_max_attempts`, `retry_initial_delay_sec`).
- Colored terminal log output when running interactively in CLI mode.

### Changed
- Database connection pool timeout increased from 10s to 30s to better accommodate slow cloud proxies.
- Default batch processing window widened from 500 records to 2,000 records, yielding ~35% higher sync throughput.

### Fixed
- Fixed parsing failure on timestamps formatted with microsecond precision (`%Y-%m-%d %H:%M:%S.%f`) (#112).
- Resolved intermittent crash on Windows when target output directory contained unicode characters in path (#128).

### Known Issues
- Parquet export sink does not support custom decimal precisions exceeding 38 digits (values are cast to standard IEEE floats).

---

## [1.0.0] - 2026-01-10

### User Impact Summary
Initial production release of the DataFlow Sync Engine, providing batch-based scheduled data synchronization between relational databases (PostgreSQL, MySQL, SQLite) and flat files.

### Added
- Core scheduled batch synchronization engine with configurable cron expressions.
- Support for PostgreSQL, MySQL, and SQLite source and destination connectors.
- Row filtering expressions using standard SQL predicates.
- Structured JSON logging to stdout and rotating log files.
- Basic CLI commands: `sync`, `validate`, `status`.

### Known Issues
- High CPU consumption observed when running against tables with >1,000,000 rows without an indexed timestamp column.
- Automatic SSL certificate authority verification cannot be bypassed without manual configuration override.

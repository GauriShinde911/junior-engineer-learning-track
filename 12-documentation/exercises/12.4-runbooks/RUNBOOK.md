# Operations Runbook: Customer Portal Service (`customer-portal-api`)

**Service Tier**: Tier 2 (Internal & External Customer Portal)  
**Primary On-Call Channel**: `#incident-customer-portal` (Slack)  
**Health Check Endpoint**: `https://portal-api.internal.acme.com/healthz`  
**Hosting Environment**: Linux systemd service on Ubuntu 22.04 LTS behind Nginx reverse proxy

---

## 1. Deployment Procedure

Follow these exact steps during scheduled deployment windows.

### 1.1 Pre-Deployment Verification
1. Ensure all integration tests on `main` branch have passed in CI/CD.
2. Verify target release tag (e.g. `v1.4.2`).
3. Check database backup status:
   ```bash
   ssh ops@db-primary.internal "sudo -u postgres pg_dump -Fc portal_db > /backups/portal_db_pre_deploy_$(date +%Y%m%d%H%M).dump"
   ```

### 1.2 Deployment Steps
1. SSH into the application host:
   ```bash
   ssh deploy@app-01.portal.internal
   ```
2. Navigate to deployment root and pull release tag:
   ```bash
   cd /opt/customer-portal-api
   git fetch --tags
   git checkout tags/v1.4.2
   ```
3. Activate virtual environment and update dependencies:
   ```bash
   source venv/bin/activate
   pip install --no-cache-dir -r requirements.txt
   ```
4. Run pending database migrations:
   ```bash
   python -m alembic upgrade head
   ```
5. Restart systemd application service:
   ```bash
   sudo systemctl restart customer-portal.service
   ```

### 1.3 Post-Deployment Verification (Smoke Test)
1. Verify systemd unit status:
   ```bash
   sudo systemctl status customer-portal.service
   ```
2. Query health check endpoint:
   ```bash
   curl -f -s http://localhost:8000/healthz | jq .
   ```
   *Expected response*: `{"status": "healthy", "database": "connected", "version": "v1.4.2"}`
3. Tail live application logs for unhandled startup tracebacks:
   ```bash
   sudo journalctl -u customer-portal.service -n 50 -f
   ```

---

## 2. Common Failure Scenarios & Troubleshooting

### Scenario 1: HTTP 502 Bad Gateway / Service Crashing on Boot
- **Symptoms**: Nginx returns HTTP 502 to users. `systemctl status` shows `failed (Result: exit-code)` with restart loops.
- **Root Cause**: Database credentials rotated or PostgreSQL unreachable on port 5432.
- **Diagnostic Commands**:
  ```bash
  sudo journalctl -u customer-portal.service -n 100 --no-pager | grep -i "OperationalError"
  nc -zv db-primary.internal 5432
  ```
- **Remediation**:
  1. If network check fails, verify VPC security groups and database host status.
  2. If credentials failed, check `/etc/customer-portal/portal.env` and refresh credentials from vault:
     ```bash
     sudo vault read secret/portal-api/production > /etc/customer-portal/portal.env
     sudo systemctl restart customer-portal.service
     ```

---

### Scenario 2: High Error Spike (HTTP 500) & Disk Full on `/var/log`
- **Symptoms**: Alert triggered: `DiskSpaceLow` (> 95% on `/`). API writes fail with `OSError: [Errno 28] No space left on device`.
- **Diagnostic Commands**:
  ```bash
  df -h /
  du -sh /var/log/customer-portal/* | sort -hr | head -n 5
  ```
- **Remediation**:
  1. Rotate or archive uncompressed old application log files immediately:
     ```bash
     sudo truncate -s 0 /var/log/customer-portal/debug_overflow.log
     sudo journalctl --vacuum-time=2d
     ```
  2. Confirm log rotation daemon configuration in `/etc/logrotate.d/customer-portal`.
  3. Restart application service to release locked file handles:
     ```bash
     sudo systemctl restart customer-portal.service
     ```

---

### Scenario 3: Stuck Background Queue / Redis Worker Stalling
- **Symptoms**: Customer notifications are delayed by > 30 minutes; Redis queue size steadily climbing (`portal:tasks` length > 10,000).
- **Diagnostic Commands**:
  ```bash
  redis-cli -h redis.internal.acme.com llen portal:tasks
  sudo systemctl status portal-worker.service
  ```
- **Remediation**:
  1. Inspect worker processes for frozen network sockets:
     ```bash
     sudo strace -p $(pgrep -f "portal-worker")
     ```
  2. Restart the worker pool:
     ```bash
     sudo systemctl restart portal-worker.service
     ```
  3. If unacknowledged poison pills exist in the queue, move failed payloads to Dead Letter Queue (DLQ):
     ```bash
     python -m scripts.drain_poison_pills --queue portal:tasks --dlq portal:dlq
     ```

---

## 3. Emergency Rollback Procedure

If severe defects, memory leaks, or unrecoverable bugs are identified post-deployment:

1. **Revert Service Code to Prior Tag**:
   ```bash
   cd /opt/customer-portal-api
   git checkout tags/v1.4.1
   ```
2. **Revert Database Migrations (if applicable)**:
   ```bash
   source venv/bin/activate
   # Downgrade by 1 revision
   python -m alembic downgrade -1
   ```
3. **Restart Application Services**:
   ```bash
   sudo systemctl restart customer-portal.service portal-worker.service
   ```
4. **Confirm Health**:
   ```bash
   curl -f http://localhost:8000/healthz
   ```
5. **Post Incident Notice**: Notify `#incident-customer-portal` that rollback to `v1.4.1` is complete and operational.

---

## 4. Escalation Path

If following the procedures above does not resolve the incident within **15 minutes**:

| Escalation Level | Contact Role | When to Escalate | Channel |
|---|---|---|---|
| **Tier 1** | Primary On-Call Engineer | Initial triage, deployment failures, restarts | PagerDuty: `portal-primary` |
| **Tier 2** | Database Administrator / Backend Lead | Corrupted migrations, deadlocks, persistent 500 spikes | `#data-infrastructure` / PagerDuty: `backend-lead` |
| **Tier 3** | VP of Engineering & Security Lead | Data breach, prolonged downtime (>30 min), data loss | `#incident-command` / Emergency Phone Tree |

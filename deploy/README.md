# BorsaTrust — Two-VM Deployment Guide

> **Target OS:** Ubuntu 22.04 / 24.04 LTS on both VMs (VirtualBox, VMware, KVM, or cloud)  
> **CI Status:** [![CI — BorsaTrust Backend & Frontend](https://github.com/Mouhadjer20/Borsa-Database-Security-Assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/Mouhadjer20/Borsa-Database-Security-Assessment/actions/workflows/ci.yml)

---

## Architecture & Network Topology

```text
                     ┌───────────────────────────────────┐
  Browser / Attacker │        VM1 — Application Server    │
  ──────────────────▶│        IP: 192.168.56.3            │
                     │                                   │
                     │  Nginx :80                        │
                     │   ├─ /         → React SPA (dist) │
                     │   └─ /api/     → FastAPI Uvicorn  │
                     │                                   │
                     │  FastAPI :8000 (127.0.0.1)        │
                     └─────────────────┬─────────────────┘
                                       │ PostgreSQL :5432
                                       │ (UFW firewall: VM1 only)
                     ┌─────────────────▼─────────────────┐
                     │        VM2 — Database Server      │
                     │        IP: 192.168.56.2           │
                     │                                   │
                     │  PostgreSQL 16/18                 │
                     │  DB: borsa_db                     │
                     │  Roles: app_writer (read/write)   │
                     │         app_readonly (read-only)  │
                     └───────────────────────────────────┘
```

---

## Network Prerequisites (VirtualBox Setup)

> ⚠️ **Important VirtualBox Note:**
> In VirtualBox's default **NAT** adapter mode, every VM receives the isolated IP `10.0.2.15`. In default NAT mode, VMs **cannot ping or connect to each other**.

**To enable direct communication between VM1 and VM2:**
1. In VirtualBox VM Settings for **both** VMs:
   * Go to **Network** ➔ **Adapter 2**.
   * Check **Enable Network Adapter**.
   * Attached to: **Host-Only Adapter** (e.g., `vboxnet0` or `VirtualBox Host-Only Ethernet Adapter`).
2. Boot the VMs and check their assigned IPs using `ip a` or `hostname -I`.
   * Typically: VM2 = `192.168.56.2`, VM1 = `192.168.56.3`.

---

## Deployment Steps (Overview)

| Stage | VM | Script | Purpose |
| :---: | :--- | :--- | :--- |
| **1** | **VM2 — Database** | `deploy/vm2-db-server/setup.sh` | PostgreSQL, `borsa_db`, schemas, roles, seeds, UFW firewall restricted to VM1 |
| **2** | **VM1 — App Server** | `deploy/vm1-app-server/setup.sh` | Python venv, Node/Vite build, FastAPI systemd service, Nginx reverse proxy on `:80` |

> **Always run Stage 1 (VM2) before Stage 2 (VM1)**, as the application backend validates database connectivity during initialization.

---

## Step 1 — Set Up VM2 (Database Server)

SSH into **VM2** (`192.168.56.2`) and run:

```bash
cd BorsaTrust-Database-Security-Assessment
git pull origin main

sudo bash deploy/vm2-db-server/setup.sh \
    --app-ip 192.168.56.3 \
    --db-password aissa123
```

> Replace `192.168.56.3` with your actual VM1 IP and choose your desired password.

### What happens automatically:
- Installs PostgreSQL and sets `listen_addresses = '*'`.
- Configures `pg_hba.conf` using tagged delimiter blocks to allow `app_writer` and `app_readonly` strictly from VM1's IP.
- Creates `borsa_db` database and grants least-privilege roles (`SELECT, INSERT` on `security_audit`).
- Applies `expected-schema.sql` and loads `seed-data.sql` with precomputed bcrypt hashes.
- Configures UFW firewall (port 5432 open **only** to VM1).
- Saves credentials to `deploy/vm2-db-server/db-credentials.txt`.

---

## Step 2 — Set Up VM1 (Application Server)

SSH into **VM1** (`192.168.56.3`) and run:

```bash
cd BorsaTrust-Database-Security-Assessment
git pull origin main

sudo bash deploy/vm1-app-server/setup.sh \
    --db-host 192.168.56.2 \
    --db-pass aissa123 \
    --frontend-origin http://192.168.56.3
```

> Replace `192.168.56.2` with your VM2 IP, and `192.168.56.3` with your VM1 IP.

### What happens automatically:
- Selects a stable Python version (`python3.12` / `3.11` / `3.13`), automatically fetching `python3.12` if Python 3.14+ is present.
- Creates `/opt/borsa` and sets up a dedicated virtual environment with `--no-cache-dir`.
- Builds the React frontend with Vite using `--legacy-peer-deps`.
- Generates `/opt/borsa/application/backend/.env` with production settings and secure JWT secret.
- Installs and starts the `borsa-backend` systemd service (Uvicorn, 2 workers).
- Configures Nginx to serve static React assets on port `80` and reverse proxy `/api/` to `127.0.0.1:8000`.
- Enables UFW firewall for SSH and Nginx (`80/tcp`).

---

## Step 3 — Verification

### Automated Health Check
From your host workstation or Kali audit machine:

```bash
bash deploy/check.sh 192.168.56.3
```

Expected output:
```text
=== BorsaTrust Health Check — http://192.168.56.3 ===

  ✓ GET /api/health → 200
  ✓ GET / (frontend) → 200
  ✓ POST /api/auth/login (bad creds) → 401
  ✓ GET /api/auth/search?q=test → 401 (endpoint exists)
  ✓ GET /api/diagnostics/db-ping?host=127.0.0.1&port=5432 → 401 (endpoint exists)

Result: 5 passed, 0 failed
All checks passed ✓
```

### Direct Login & Audit Test
Test login from CLI:
```bash
curl -i -X POST http://192.168.56.3/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"bob1234"}'
```

Verify audit log insertion on VM2:
```bash
sudo -u postgres psql -d borsa_db -c "
  SELECT event_id, actor, action, resource, timestamp 
  FROM security_audit 
  ORDER BY timestamp DESC 
  LIMIT 5;
"
```

---

## Test Accounts & Credentials

The database comes pre-seeded with 5 active test accounts:

| Username | Password | Role | Customer Profile | Checking Balance |
| :--- | :--- | :--- | :--- | :--- |
| `alice` | `alice1234` | customer | Alice Nguyen | $12,450.00 |
| `bob` | `bob1234` | customer | Bob Markov | $5,700.00 |
| `charlie` | `charlie1234` | customer | Charlie Durand | $22,100.00 |
| `diana` | `diana1234` | customer | Diana Prince | $3,300.00 |
| `admin` | `adminpass1` | admin | Administrator | System Admin |

---

## System Management Commands

### On VM1 (Application Server)
```bash
# Check backend service status
systemctl status borsa-backend

# Follow live backend logs
journalctl -u borsa-backend -f

# Restart backend service
sudo systemctl restart borsa-backend

# Restart Nginx
sudo systemctl restart nginx

# Redeploy after Git code updates
sudo bash deploy/vm1-app-server/deploy.sh
```

### On VM2 (Database Server)
```bash
# Access database console
sudo -u postgres psql -d borsa_db

# Manual database backup
sudo bash deploy/vm2-db-server/backup.sh

# Reset and re-seed database (for CTF round resets)
sudo -u postgres psql -d borsa_db -c "
  TRUNCATE security_audit, transactions, bank_accounts, customers, app_users RESTART IDENTITY CASCADE;
"
cat database/seed-data.sql | sudo -u postgres psql -d borsa_db
```

---

## Embedded CTF Vulnerabilities Reference

The system diagnostics tools embedded in the frontend (`/diagnostics`) expose 4 real-world security vulnerabilities:

| # | Vulnerability | Endpoint | Hidden Weakness |
| :---: | :--- | :--- | :--- |
| **1** | **SQL Injection (CWE-89)** | `GET /api/auth/search?q=` | Unescaped string interpolation in user directory lookup |
| **2** | **BOLA / IDOR (CWE-284)** | `GET /api/accounts/lookup/{ref}` | Direct account ID reference without customer ownership validation |
| **3** | **Excessive Privileges (CWE-250)** | `GET /api/transactions/export` | Discloses database user, backend PID, and engine version in `session_metadata` |
| **4** | **SSRF / Net Exposure (CWE-668)** | `GET /api/diagnostics/db-ping` | Unrestricted host and port TCP socket probe |

---

## Troubleshooting

| Problem | Root Cause | Solution |
| :--- | :--- | :--- |
| `psql: Permission denied` | `postgres` OS user cannot read `/home/ubuntu/` | Fixed: setup scripts stream SQL via stdin (`cat file \| sudo -u postgres psql`) |
| `audit_insert_failed / ProgrammingError` | `app_writer` lacked `SELECT` privilege on `security_audit` for `RETURNING` clause | Fixed in repo: run `sudo -u postgres psql -d borsa_db -c "GRANT SELECT, INSERT ON security_audit TO app_writer;"` |
| `PendingRollbackError` on login | Unhandled flush failure poisoned the transaction | Fixed in repo: audit inserts now run in an isolated savepoint (`session.begin_nested()`) |
| `Bad CRC-32 / BadZipFile` | Truncated pip wheel cache on fresh VMs | Fixed: setup script purges pip cache and passes `--no-cache-dir --retries 5` |
| Python 3.14 wheel errors | Native binary wheels not yet built for Python 3.14 | Fixed: setup script detects 3.14 and installs stable `python3.12` |
| `ERESOLVE` during frontend build | Vite 8 vs React plugin peer dependency conflict | Fixed: `.npmrc` sets `legacy-peer-deps=true` and build runs with `--legacy-peer-deps` |
| Connection refused on port 5432 | VM2 firewall or `listen_addresses` | Verify VM2 `ufw status` allows VM1 IP; verify `listen_addresses = '*'` in `postgresql.conf` |
| VMs cannot ping each other on `10.0.2.15` | Default VirtualBox NAT mode isolates VMs | Configure VirtualBox **Host-Only Adapter** on Adapter 2 for both VMs |

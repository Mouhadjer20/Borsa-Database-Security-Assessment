# BorsaTrust — Two-VM Deployment Guide

> **Target:** Ubuntu 22.04 / 24.04 LTS on both VMs (VirtualBox, VMware, KVM, cloud — any hypervisor)

## Architecture

```
                     ┌──────────────────────────┐
  Browser / Attacker │   VM1 — App Server        │
  ──────────────────▶│   IP: 192.168.1.5      │
                     │                           │
                     │  Nginx :80                │
                     │   ├─ /         → React    │
                     │   └─ /api/     → Uvicorn  │
                     │                           │
                     │  FastAPI :8000 (localhost) │
                     └────────────┬──────────────┘
                                  │ PostgreSQL :5432
                                  │ (firewall: VM1 only)
                     ┌────────────▼──────────────┐
                     │   VM2 — Database Server   │
                     │   IP: 192.168.1.5      │
                     │                           │
                     │  PostgreSQL 16            │
                     │  DB: borsa_db             │
                     │  Roles: app_writer        │
                     │         app_readonly      │
                     └───────────────────────────┘
```

## Deployment Method (overview)

The project is deployed in two stages, one script per VM:

| Stage | VM | Script | Purpose |
| ----- | -- | ------ | ------- |
| 1 | VM2 — Database Server | `deploy/vm2-db-server/setup.sh` | PostgreSQL 16, `borsa_db`, roles (`app_writer` / `app_readonly`), schema + seed data, firewall restricted to VM1 |
| 2 | VM1 — Application Server | `deploy/vm1-app-server/setup.sh` | Python 3.11 + Node.js 20 + Nginx, React build, FastAPI backend (systemd), Nginx reverse proxy on `:80`, `.env` with DB credentials |

**Order matters:** always run Stage 1 (VM2) before Stage 2 (VM1), because VM1 needs VM2's IP and database password.

> **Cross-platform note:** the setup scripts now detect the host IP portably (Linux `ip`, macOS/BSD `ifconfig`, or Python fallback), so they can be tested on macOS as well as the target Ubuntu VMs. The `hostname -I` command shown below is only for use **inside** the Ubuntu VMs.

After both stages complete, run `bash deploy/check.sh <VM1_IP>` to verify, then open `http://<VM1_IP>` in a browser.

Full per-VM procedures follow.

---

## Prerequisites

- Both VMs on the same network (host-only or bridged adapter)
- SSH access to both VMs
- Project cloned/copied to both VMs (or only VM1 — VM2 setup uses SQL files)

---

## Step 1 — Set Up VM2 (Database Server)

SSH into VM2 and run:

```bash
cd BorsaTrust-Database-Security-Assessment
sudo bash deploy/vm2-db-server/setup.sh \
    --app-ip 192.168.1.5 \
    --db-password YourStrongPassword
```

> Replace `192.168.1.5` with VM1's actual IP and choose a strong password.

**What it does:**
- Installs PostgreSQL 16
- Creates `borsa_db` database with `app_writer` and `app_readonly` roles
- Runs schema + seed SQL (5 test users, accounts, transactions)
- Configures `pg_hba.conf` to allow connections only from VM1
- Configures UFW firewall (port 5432 open to VM1 only)
- Writes `deploy/vm2-db-server/db-credentials.txt` with the generated passwords

**Note the DB VM's IP:**
```bash
hostname -I
```

---

## Step 2 — Set Up VM1 (Application Server)

SSH into VM1 and run:

```bash
cd BorsaTrust-Database-Security-Assessment
sudo bash deploy/vm1-app-server/setup.sh \
    --db-host 192.168.1.5 \
    --db-pass YourStrongPassword \
    --frontend-origin http://192.168.1.5
```

> Replace `192.168.1.5` with VM2's actual IP, `YourStrongPassword` with what you set in Step 1.

**What it does:**
- Installs Python 3.11, Node.js 20, Nginx
- Copies project to `/opt/borsa/`
- Creates Python venv + installs all backend dependencies
- Builds the React frontend with Vite
- Writes `/opt/borsa/application/backend/.env` (auto-generated JWT secret)
- Installs + starts `borsa-backend` systemd service (Uvicorn, 2 workers)
- Configures Nginx: serves frontend on `:80`, proxies `/api/` to Uvicorn
- Configures UFW firewall (ports 22, 80, 443)

---

## Step 3 — Verify the Deployment

From your host machine (or any attacker VM):

```bash
bash deploy/check.sh 192.168.1.5
```

Expected output:
```
  ✓ GET /api/health → 200
  ✓ GET / (frontend) → 200
  ✓ POST /api/auth/login (bad creds) → 401
  ✓ GET /api/auth/search?q=test → 401
  ✓ GET /api/diagnostics/db-ping?host=127.0.0.1&port=5432 → 401

Result: 5 passed, 0 failed
```

---

## Step 4 — Log In

Open `http://192.168.1.5` in a browser.

| Username  | Password      | Role     |
| --------- | ------------- | -------- |
| `alice`   | `alice1234`   | customer |
| `bob`     | `bob1234`     | customer |
| `charlie` | `charlie1234` | customer |
| `diana`   | `diana1234`   | customer |
| `admin`   | `adminpass1`  | admin    |

---

## Service Management (VM1)

```bash
# Check backend status
systemctl status borsa-backend

# Live logs
journalctl -u borsa-backend -f

# Restart backend
sudo systemctl restart borsa-backend

# Restart nginx
sudo systemctl restart nginx

# Redeploy after code changes
sudo bash deploy/vm1-app-server/deploy.sh
```

---

## Database Management (VM2)

```bash
# Connect to the database
sudo -u postgres psql -d borsa_db

# Manual backup
sudo bash deploy/vm2-db-server/backup.sh

# Schedule nightly backups at 02:00
echo "0 2 * * * root bash /path/to/deploy/vm2-db-server/backup.sh" \
  | sudo tee /etc/cron.d/borsa-backup

# Reset and re-seed (useful for CTF resets)
sudo -u postgres psql -d borsa_db -c "
  TRUNCATE app_users, customers, bank_accounts, transactions,
           security_audit RESTART IDENTITY CASCADE;
"
sudo -u postgres psql -d borsa_db -f database/seed-data.sql
```

---

## CTF Endpoints Reference

All 4 vulnerable endpoints look like normal banking features:

| Path                         | Method | Auth       | Hidden Vuln                   |
| ---------------------------- | ------ | ---------- | ----------------------------- |
| `/api/auth/search?q=`        | GET    | ✅ Required | SQL Injection (CWE-89)        |
| `/api/accounts/lookup/{ref}` | GET    | ✅ Required | BOLA/IDOR (CWE-284)           |
| `/api/transactions/export`   | GET    | ✅ Required | Excessive Privs (CWE-250)     |
| `/api/diagnostics/db-ping`   | GET    | ✅ Required | SSRF / Net Exposure (CWE-668) |

Access them via the **System Diagnostics** page in the app sidebar after login.

---

## Troubleshooting

| Problem                | Fix                                                                       |
| ---------------------- | ------------------------------------------------------------------------- |
| Backend not starting   | `journalctl -u borsa-backend -n 100`                                      |
| DB connection refused  | Check VM2 `ufw status`, confirm port 5432 open to VM1                     |
| DB auth failure        | Verify password in `/opt/borsa/application/backend/.env` matches VM2 role |
| Frontend 404 on routes | Confirm nginx `try_files $uri /index.html` is present                     |
| CORS errors            | Add VM1's IP to `CORS_ORIGINS` in `.env`, restart backend                 |
| npm build fails        | `node --version` must be ≥20; re-run NodeSource install                   |


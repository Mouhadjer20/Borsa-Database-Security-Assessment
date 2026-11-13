# Borsa — Financial Platform & Database Security CTF

[![CI — BorsaTrust Backend & Frontend](https://github.com/Mouhadjer20/Borsa-Database-Security-Assessment/actions/workflows/ci.yml/badge.svg)](https://github.com/Mouhadjer20/Borsa-Database-Security-Assessment/actions/workflows/ci.yml)

> **⚠️ IMPORTANT:** This project is exclusively for educational purposes and authorized security testing within an isolated virtual laboratory using synthetic financial data. Never deploy against real systems or databases.

## Overview

Borsa simulates a fictional financial institution as a full-stack web application designed for two purposes:

1. **Financial application** — A professional dashboard for authenticated users to view accounts, balances, and transactions.
2. **Black-box security CTF** — Four real security vulnerabilities are embedded directly into the application's normal API surface. There is no separate "lab" panel — the vulnerabilities look and behave like legitimate features. Discover and exploit them as a penetration tester would.

---

## CTF — 4 Hidden Vulnerabilities

The vulnerabilities are injected into real application endpoints. No labels, no "variant A/B" — this is **black-box**. You are expected to enumerate the API, find the weaknesses, and demonstrate exploitation.

| # | CWE | Vulnerability | Hidden Feature | Endpoint |
|---|-----|--------------|----------------|----------|
| 1 | CWE-89 | SQL Injection | User search for transfer lookup | `GET /api/auth/search?q=...` |
| 2 | CWE-284 | Broken Object-Level Authorization (BOLA/IDOR) | Account reference lookup | `GET /api/accounts/lookup/{id}` |
| 3 | CWE-250 | Excessive Database Privileges | Transaction export with audit metadata | `GET /api/transactions/export` |
| 4 | CWE-668 | Database Network Exposure (SSRF) | DB connectivity diagnostics | `GET /api/diagnostics/db-ping?host=...` |

> **Rules of engagement:** Only test against this application running in your isolated lab. Never use these techniques against real systems.

### CTF Hints (Expand to Read)

<details>
<summary>Hint 1 — SQL Injection</summary>

The user search endpoint at `GET /api/auth/search?q=<input>` builds a raw SQL query using string formatting. Try injecting a payload in the `q` parameter to manipulate the WHERE clause and extract data beyond your own user record.

**Classic payloads to try:**
- `q=' OR '1'='1` — returns all users
- `q=alice' UNION SELECT table_name, table_schema, '3' FROM information_schema.tables--`

</details>

<details>
<summary>Hint 2 — BOLA / IDOR</summary>

The account lookup endpoint `GET /api/accounts/lookup/{account_ref}` is intended for verifying a transfer recipient's account. It accepts any numeric account ID but does **not** verify that the account belongs to the authenticated user.

Try accessing account IDs that don't belong to your user (e.g., `/api/accounts/lookup/1`, `/api/accounts/lookup/2`, etc.).

</details>

<details>
<summary>Hint 3 — Excessive Database Privileges</summary>

The transaction export endpoint `GET /api/transactions/export` returns a `session_metadata` field in its response. Inspect this field — it leaks the database user identity, server PID, and PostgreSQL version string.

Use this information to understand the DB role the application runs as, then assess whether that role has permissions beyond what is strictly necessary (e.g., access to `pg_roles`, `information_schema`, or other system catalogs).

</details>

<details>
<summary>Hint 4 — Network Exposure / SSRF</summary>

The diagnostics endpoint `GET /api/diagnostics/db-ping?host=<host>&port=<port>` probes TCP connectivity. The `host` and `port` parameters are taken directly from your request with no restriction.

Use this to scan internal network segments from the application server's perspective — particularly the `192.168.200.x` DB-NET range that is not directly reachable from the AUDIT-NET.

**Example recon payloads:**
- `?host=192.168.200.30&port=5432` — probe the DB server directly
- `?host=192.168.200.1&port=22` — check for SSH
- `?host=127.0.0.1&port=8080` — check for local services

</details>

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Database | PostgreSQL 18.x |
| ORM | SQLAlchemy 2 (async) |
| DB Driver | Psycopg 3 |
| Validation | Pydantic v2 |

---

## Virtual Laboratory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ISOLATED LAB                         │
│                                                             │
│  ┌──────────────┐  AUDIT-NET   ┌──────────────────┐        │
│  │  VM1: Kali   │◄────────────►│  VM2: App Server │        │
│  │ 192.168.100.10│             │  192.168.100.20   │        │
│  │  Audit tools │             │  :192.168.200.20  │        │
│  └──────────────┘             └────────┬─────────┘        │
│                                        │ DB-NET            │
│                                        ▼                   │
│                               ┌──────────────────┐        │
│                               │  VM3: DB Server  │        │
│                               │  192.168.200.30   │        │
│                               │  PostgreSQL 18.x  │        │
│                               └──────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

- **AUDIT-NET** (`192.168.100.0/24`): Kali workstation ↔ App Server
- **DB-NET** (`192.168.200.0/24`): App Server ↔ DB Server (isolated, not directly reachable from Kali)

---

## Project Structure

```
Borsa/
├── README.md
├── requirements.txt          # Root-level convenience copy
├── requirement.txt           # Alias
├── .gitignore
├── documentation/            # Research and architecture docs
│   ├── 01-project-charter.md
│   ├── 02-research-questions.md
│   ├── 03-scope-and-rules-of-engagement.md
│   ├── 04-architecture.md
│   ├── 05-threat-model.md
│   ├── 06-database-design.md
│   ├── 07-methodology.md
│   ├── 08-security-experiments.md
│   ├── 09-results-and-analysis.md
│   └── 10-final-report.md
├── infrastructure/           # VM and network configuration
│   ├── vm-specifications/
│   ├── network-topology/
│   ├── firewall/
│   └── database-configuration/
├── database/                 # DB schema reference and policies
│   ├── schema-reference/
│   ├── roles/
│   ├── policies/
│   └── audit/
├── application/
│   ├── backend/              # FastAPI application
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/         # Config, security, logging
│   │   │   ├── database/     # Engine, session
│   │   │   ├── models/       # SQLAlchemy ORM models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── repositories/ # DB access layer
│   │   │   ├── services/     # Business logic
│   │   │   ├── api/          # Route handlers (vulnerabilities hidden here)
│   │   │   │   ├── auth.py          # Login, logout, /search (SQLi)
│   │   │   │   ├── accounts.py      # Accounts + /lookup (BOLA)
│   │   │   │   ├── transactions.py  # Transactions + /export (CWE-250)
│   │   │   │   ├── diagnostics.py   # /db-ping (SSRF/CWE-668)
│   │   │   │   └── health.py
│   │   │   ├── middleware/
│   │   │   └── security/
│   │   ├── tests/
│   │   │   ├── test_accounts.py
│   │   │   ├── test_auth.py
│   │   │   └── test_ctf.py    # CTF route & schema tests
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── .env               # Local dev config (not committed)
│   └── frontend/              # React application
│       └── src/
├── tests/                     # Integration and security tests
└── evidence/                  # Experiment results and logs
```

---

## Quick Start

### Prerequisites

- PostgreSQL 18.x configured (see [infrastructure docs](infrastructure/database-configuration/postgresql-config.md))
- Python 3.11+
- Node.js 20+ and npm/pnpm

### Backend Setup

```bash
cd BorsaTrust-Database-Security-Assessment

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cd application/backend
cp .env.example .env
# Edit .env with your database credentials

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd application/frontend

# Install dependencies
pnpm install   # or: npm install

# Start development server
pnpm dev       # or: npm run dev
```

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Run Tests

```bash
cd application/backend
../../.venv/bin/pytest -v
```

Expected: **13 tests passed**

---

## 🚀 Two-VM Automated Deployment

Automated scripts for deploying the platform across two Linux VMs (**VM1 Application Server** + **VM2 Database Server**) are located under [`deploy/`](deploy/README.md).

### Recommended VirtualBox Network Topology
- **VM2 (Database Server):** `192.168.56.2` (PostgreSQL 16, firewall restricted to VM1)
- **VM1 (Application Server):** `192.168.56.3` (FastAPI backend + Nginx + React SPA on port 80)
- **Network Mode:** VirtualBox **Host-Only Adapter** (Adapter 2 on both VMs, e.g. `vboxnet0`)

### Step 1: On VM2 (Database Server — 192.168.56.2)
```bash
cd BorsaTrust-Database-Security-Assessment
git pull origin main

sudo bash deploy/vm2-db-server/setup.sh \
    --app-ip 192.168.56.3 \
    --db-password aissa123
```

### Step 2: On VM1 (Application Server — 192.168.56.3)
```bash
cd BorsaTrust-Database-Security-Assessment
git pull origin main

sudo bash deploy/vm1-app-server/setup.sh \
    --db-host 192.168.56.2 \
    --db-pass aissa123 \
    --frontend-origin http://192.168.56.3
```

### Step 3: Verify Deployment & Connectivity
Run the automated test suite from your host machine or audit VM:
```bash
bash deploy/check.sh 192.168.56.3
```

Verify authentication and audit persistence:
```bash
# Test login via API
curl -i -X POST http://192.168.56.3/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"bob1234"}'

# Verify audit trail on VM2
sudo -u postgres psql -d borsa_db -c "SELECT event_id, actor, action, resource, timestamp FROM security_audit ORDER BY timestamp DESC LIMIT 3;"
```

### Seeded Test Credentials

| Username | Password | Role | Customer Profile | Checking Balance |
| :--- | :--- | :--- | :--- | :--- |
| `alice` | `alice1234` | customer | Alice Nguyen | $12,450.00 |
| `bob` | `bob1234` | customer | Bob Markov | $5,700.00 |
| `charlie` | `charlie1234` | customer | Charlie Durand | $22,100.00 |
| `diana` | `diana1234` | customer | Diana Prince | $3,300.00 |
| `admin` | `adminpass1` | admin | Administrator | System Admin |

For full deployment documentation, service commands, and troubleshooting guides, see [deploy/README.md](deploy/README.md).

---

## API Reference

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/login` | No | Login with username + password |
| `POST` | `/api/auth/logout` | Cookie | Clear session |
| `GET` | `/api/auth/me` | Cookie | Current user identity |
| `GET` | `/api/auth/search?q=` | Cookie | Search users by name |

### Accounts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/accounts` | Cookie | List my accounts |
| `GET` | `/api/accounts/{id}` | Cookie | Get specific account (ownership enforced) |
| `GET` | `/api/accounts/lookup/{ref}` | Cookie | Account reference lookup |

### Transactions

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/transactions` | Cookie | All transactions across my accounts |
| `GET` | `/api/accounts/{id}/transactions` | Cookie | Transactions for a specific account |
| `GET` | `/api/transactions/export` | Cookie | Export with session metadata |

### Diagnostics

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/diagnostics/db-ping` | Cookie | Check DB connectivity |
| `GET` | `/api/diagnostics/server-info` | Cookie (admin/employee) | Server config info |

### Health

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/health` | No | Application health status |

---

## Database Roles

| Role | Purpose | Privileges |
|------|---------|-----------|
| `app_readonly` | Secure read operations | SELECT on financial tables |
| `app_writer` | Limited write operations | SELECT + INSERT on specific tables |
| `auditor` | Security inspection | SELECT on all + audit tables |
| `migration_role` | Schema management | DDL permissions (not used at runtime) |
| `db_owner` | Object ownership | Schema owner (not used at runtime) |

---

## Security Research Scenarios (CWE Reference)

| # | CWE | Title | Location |
|---|-----|-------|----------|
| 1 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | SQL Injection | `app/api/auth.py` → `search_users()` |
| 2 | [CWE-284](https://cwe.mitre.org/data/definitions/284.html) | Broken Object-Level Authorization | `app/api/accounts.py` → `lookup_account_by_ref()` |
| 3 | [CWE-250](https://cwe.mitre.org/data/definitions/250.html) | Execution with Unnecessary Privileges | `app/api/transactions.py` → `export_transactions()` |
| 4 | [CWE-668](https://cwe.mitre.org/data/definitions/668.html) | Exposure of Resource to Wrong Sphere | `app/api/diagnostics.py` → `db_connectivity_check()` |

---

## Documentation

| Document | Description |
|----------|-------------|
| [Project Charter](documentation/01-project-charter.md) | Scope, objectives, authorized use |
| [Research Questions](documentation/02-research-questions.md) | Research questions and hypotheses |
| [Rules of Engagement](documentation/03-scope-and-rules-of-engagement.md) | Lab rules and boundaries |
| [Architecture](documentation/04-architecture.md) | System and network architecture |
| [Threat Model](documentation/05-threat-model.md) | STRIDE threat model |
| [Database Design](documentation/06-database-design.md) | Schema reference and DB roles |
| [Methodology](documentation/07-methodology.md) | Research and experimental method |
| [Security Experiments](documentation/08-security-experiments.md) | Experiment procedures |
| [Results Template](documentation/09-results-and-analysis.md) | Results recording template |
| [Final Report](documentation/10-final-report.md) | Report template |

---

## Important Constraints

1. **Do not modify the database schema** — the DB is managed separately
2. **Do not use real financial data** — synthetic data only
3. **Do not test against real systems** — isolated lab only
4. **All DB operations** must pass through the FastAPI backend
5. **Do not expose the application** outside the isolated lab network

---

## License

This project is for educational and authorized security research purposes only. All financial data is synthetic and fictional. Unauthorized use against real systems is prohibited.

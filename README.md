# Borsa — Educational Financial Web Application and Database Security Assessment

> **⚠️ IMPORTANT:** This project is exclusively for educational purposes and authorized security testing within an isolated virtual laboratory using synthetic financial data. Never deploy vulnerable lab functionality against real systems or databases.

## Overview

Borsa simulates a fictional financial institution as a full-stack web application, designed for:

1. **Financial application:** A professional dashboard for authenticated users to view accounts, balances, and transactions.
2. **Cybersecurity research platform:** A controlled environment for demonstrating, testing, and comparing common web application and database security vulnerabilities.

## Primary Security Research Scenarios

| # | Scenario | CWE |
|---|---|---|
| 1 | SQL Injection (SQLi) | CWE-89 |
| 2 | Excessive Database Privileges | CWE-250 |
| 3 | Broken Authorization (BOLA/IDOR) | CWE-284 |
| 4 | Database Network Exposure | CWE-668 |

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL 18.x |
| ORM | SQLAlchemy 2 (async) |
| DB Driver | Psycopg 3 |
| Validation | Pydantic v2 |

## Virtual Laboratory Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ISOLATED LAB                             │
│                                                                 │
│  ┌──────────────┐  AUDIT-NET   ┌──────────────────┐            │
│  │   VM1: Kali  │◄────────────►│  VM2: App Server │            │
│  │  192.168.100.10│            │  192.168.100.20   │            │
│  │  Audit tools │             │  :192.168.200.20  │            │
│  └──────────────┘             └────────┬─────────┘            │
│                                        │ DB-NET               │
│                                        ▼                       │
│                               ┌──────────────────┐            │
│                               │  VM3: DB Server  │            │
│                               │  192.168.200.30   │            │
│                               │  PostgreSQL 18.x  │            │
│                               └──────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

- **AUDIT-NET** (`192.168.100.0/24`): Kali workstation ↔ App Server
- **DB-NET** (`192.168.200.0/24`): App Server ↔ DB Server (isolated)

## Project Structure

```
Borsa/
├── README.md
├── .gitignore
├── documentation/           # Research and architecture docs
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
├── infrastructure/          # VM and network configuration
│   ├── vm-specifications/
│   ├── network-topology/
│   ├── firewall/
│   └── database-configuration/
├── database/               # DB schema reference and policies
│   ├── schema-reference/
│   ├── roles/
│   ├── policies/
│   └── audit/
├── application/
│   ├── backend/            # FastAPI application
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/
│   │   │   ├── database/
│   │   │   ├── models/
│   │   │   ├── schemas/
│   │   │   ├── repositories/
│   │   │   ├── services/
│   │   │   ├── api/
│   │   │   ├── middleware/
│   │   │   ├── security/
│   │   │   └── lab/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── .env.example
│   └── frontend/           # React application
│       └── src/
├── tests/                  # Integration and security tests
└── evidence/               # Experiment results and logs
```

## Quick Start

### Prerequisites

- PostgreSQL 18.x database already configured (see [infrastructure docs](infrastructure/database-configuration/postgresql-config.md))
- Python 3.11+
- Node.js 20+ and pnpm

### Backend Setup

```bash
cd application/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd application/frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The frontend will be available at `http://localhost:5173`.  
The backend API will be available at `http://localhost:8000`.  
API documentation: `http://localhost:8000/docs`

## Security Modes

### Secure Mode (Default)
- Parameterized SQL queries
- Least-privilege database roles
- Server-side authorization
- Secure session management
- Input validation

Set `APP_SECURITY_MODE=secure` in `.env`.

### Vulnerable Lab Mode
- Requires explicit configuration: `LAB_ENABLED=true`
- Requires separate lab database credentials
- Intentionally vulnerable endpoints for research
- **Never enable in production**

Set `LAB_ENABLED=true` and configure `LAB_DB_*` variables in `.env`.

## Database Roles

| Role | Purpose | Privileges |
|---|---|---|
| `app_readonly` | Secure read operations | SELECT on financial tables |
| `app_writer` | Limited write operations | SELECT + INSERT on specific tables |
| `app_vulnerable` | Overprivileged lab identity | Broad privileges for research |
| `auditor` | Security inspection | SELECT on all + audit tables |
| `migration_role` | Schema management | DDL permissions (not used at runtime) |
| `db_owner` | Object ownership | Schema owner (not used at runtime) |

## Security Experiments

See [documentation/08-security-experiments.md](documentation/08-security-experiments.md) for complete experiment procedures.

| Scenario | Endpoint | Mode |
|---|---|---|
| SQL Injection | `POST /api/lab/experiments/sqli` | Lab only |
| Excessive Privileges | `POST /api/lab/experiments/privileges` | Lab only |
| Broken Authorization | `POST /api/lab/experiments/bola` | Lab only |
| Network Exposure | `POST /api/lab/experiments/network` | Lab only |

## Important Constraints

1. **Do not modify the database schema** — the DB is managed separately
2. **Do not use real financial data** — synthetic data only
3. **Do not expose vulnerable endpoints outside the lab** — `LAB_ENABLED` must be false in production
4. **Do not connect to real databases** from vulnerable lab mode
5. **All DB operations** must pass through the FastAPI backend

## Documentation

| Document | Description |
|---|---|
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

## License

This project is for educational and authorized security research purposes only. All financial data is synthetic and fictional. Unauthorized use against real systems is prohibited.


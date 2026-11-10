# System Architecture — Borsa Security Research Platform

> **Document Version:** 1.0  
> **Classification:** Internal Research / Educational Use Only

---

## 1. Architecture Overview

Borsa is a three-tier web application deployed across a three-VM VirtualBox laboratory. The architecture deliberately mirrors a realistic production deployment to make security scenarios meaningful and transferable, while remaining entirely isolated within a controlled lab.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        HOST MACHINE (Windows)                       │
│                     Oracle VirtualBox Hypervisor                    │
│                                                                     │
│  ┌──────────────────┐          ┌──────────────────────────────────┐ │
│  │    AUDIT-NET     │          │            DB-NET                │ │
│  │  192.168.100.0/24│          │        192.168.200.0/24          │ │
│  │  (Host-Only #1)  │          │          (Host-Only #2)          │ │
│  └────────┬─────────┘          └──────────────┬───────────────────┘ │
│           │                                   │                     │
│  ┌────────▼─────────┐  ┌────────────────────-─▼──────────────────┐ │
│  │      VM1         │  │               VM2                        │ │
│  │   Kali Linux     │  │          Ubuntu App Server               │ │
│  │  AUDIT Workstation│  │   eth0: 192.168.100.20 (AUDIT-NET)      │ │
│  │  192.168.100.10  │  │   eth1: 192.168.200.20 (DB-NET)         │ │
│  │                  │  │                                          │ │
│  │  Tools:          │  │  Services:                               │ │
│  │  • nmap          │  │  • React (port 3000 or via Nginx :80)   │ │
│  │  • sqlmap        │  │  • FastAPI (port 8000)                  │ │
│  │  • Burp Suite    │  │  • Nginx reverse proxy (optional)       │ │
│  │  • psql client   │  │                                          │ │
│  │  • curl          │  │                                          │ │
│  │  • wireshark     │  │                                          │ │
│  └──────────────────┘  └────────────────────────-─────────────────┘ │
│                                       │                             │
│                              ┌────────▼──────────┐                  │
│                              │        VM3        │                  │
│                              │  Ubuntu DB Server │                  │
│                              │  192.168.200.30   │                  │
│                              │  (DB-NET only)    │                  │
│                              │                   │                  │
│                              │  Services:        │                  │
│                              │  • PostgreSQL 18.x│                  │
│                              │    port 5432      │                  │
│                              └───────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Network Segmentation

### 2.1 Network Segments

| Network | CIDR | VirtualBox Type | Purpose |
|---------|------|-----------------|---------|
| **AUDIT-NET** | `192.168.100.0/24` | Host-Only Adapter #1 | Attack/audit traffic, frontend access |
| **DB-NET** | `192.168.200.0/24` | Host-Only Adapter #2 | Backend-to-database communication only |

### 2.2 IP Address Assignments

| VM | Interface | IP Address | Network | Gateway |
|----|-----------|-----------|---------|---------|
| VM1 (Kali) | eth0 | `192.168.100.10/24` | AUDIT-NET | `192.168.100.1` (host) |
| VM2 (App) | eth0 | `192.168.100.20/24` | AUDIT-NET | `192.168.100.1` (host) |
| VM2 (App) | eth1 | `192.168.200.20/24` | DB-NET | — |
| VM3 (DB) | eth0 | `192.168.200.30/24` | DB-NET | — |

### 2.3 Segmentation Intent

The architecture enforces two critical trust boundaries:

1. **AUDIT-NET → App Server only:** VM1 (attacker) can reach VM2's application ports but has no direct route to VM3
2. **DB-NET isolated:** VM3 is unreachable from AUDIT-NET in the secure configuration; only VM2 may connect to PostgreSQL on port 5432

```
VM1 (Kali)  ──[AUDIT-NET]──▶  VM2 (App)  ──[DB-NET]──▶  VM3 (DB)
  .100.10                        .100.20/.200.20              .200.30
                                     ▲
                              Dual-homed:
                           Bridges the two segments
```

---

## 3. Application Layer Architecture

### 3.1 Three-Tier Stack

```
┌─────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                 │
│                                                     │
│   React 18 + TypeScript (Vite)                      │
│   • SPA served by Nginx or Vite dev server          │
│   • Communicates exclusively via REST API calls     │
│   • JWT stored in httpOnly cookie or localStorage   │
└──────────────────────────┬──────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────▼──────────────────────────┐
│                    APPLICATION TIER                  │
│                                                     │
│   FastAPI (Python 3.11+)                            │
│   • Uvicorn ASGI server (port 8000)                 │
│   • JWT authentication middleware                   │
│   • Business logic and authorization checks         │
│   • asyncpg / psycopg3 database driver              │
│   • Pydantic v2 request/response validation         │
└──────────────────────────┬──────────────────────────┘
                           │ SQL over TCP (port 5432)
┌──────────────────────────▼──────────────────────────┐
│                      DATA TIER                       │
│                                                     │
│   PostgreSQL 18.x                                   │
│   • Port 5432                                       │
│   • Listens on DB-NET only (192.168.200.30)         │
│   • Multiple roles (least-privilege in secure mode) │
│   • Row-Level Security (RLS) policies               │
│   • pgaudit extension for audit logging             │
└─────────────────────────────────────────────────────┘
```

### 3.2 Application Modules

| Module | Description | Location |
|--------|-------------|----------|
| `auth` | Login, registration, JWT issuance | `backend/app/auth/` |
| `accounts` | Bank account CRUD | `backend/app/accounts/` |
| `transactions` | Transaction history, transfers | `backend/app/transactions/` |
| `users` | User profile management | `backend/app/users/` |
| `admin` | Administrative operations (privileged) | `backend/app/admin/` |
| `db` | Database connection pool, session management | `backend/app/db/` |

---

## 4. Security Mode Architecture

The Borsa platform supports two deployment modes. Mode is configured via environment variables and PostgreSQL configuration.

### 4.1 Vulnerable Lab Mode

```
┌──────────────────────────────────────────────────────────────────┐
│                      VULNERABLE MODE                             │
│                                                                  │
│  ┌────────────────┐    ┌──────────────────┐    ┌─────────────┐  │
│  │  Login Form    │    │  FastAPI          │    │ PostgreSQL  │  │
│  │                │    │                  │    │             │  │
│  │ No rate limit  │───▶│ String concat SQL│───▶│ app_vuln.   │  │
│  │ Verbose errors │    │ No authz check   │    │ role:SUPER  │  │
│  │                │    │ Verbose errors   │    │ USER perms  │  │
│  └────────────────┘    └──────────────────┘    └─────────────┘  │
│                                                                  │
│  Network: pg_hba.conf allows AUDIT-NET (192.168.100.0/24)       │
│  Firewall: No iptables rules on VM3                              │
└──────────────────────────────────────────────────────────────────┘
```

| Vulnerability | Vulnerable Configuration |
|---------------|--------------------------|
| SQLi (CWE-89) | Queries built via f-string concatenation |
| Excess Privileges (CWE-250) | `app_vulnerable` role has SUPERUSER or broad GRANT ALL |
| BOLA (CWE-284) | No `account_id` ownership check in API handlers |
| Network Exposure (CWE-668) | `pg_hba.conf` host record allows `192.168.100.0/24` |

### 4.2 Secure Lab Mode

```
┌──────────────────────────────────────────────────────────────────┐
│                        SECURE MODE                               │
│                                                                  │
│  ┌────────────────┐    ┌──────────────────┐    ┌─────────────┐  │
│  │  Login Form    │    │  FastAPI          │    │ PostgreSQL  │  │
│  │                │    │                  │    │             │  │
│  │ Rate limiting  │───▶│ Parameterized SQL│───▶│ app_writer/ │  │
│  │ Generic errors │    │ Ownership check  │    │ app_readonly │  │
│  │                │    │ Generic errors   │    │ Least-priv  │  │
│  └────────────────┘    └──────────────────┘    │ + RLS       │  │
│                                                └─────────────┘  │
│  Network: pg_hba.conf allows only 192.168.200.20/32            │
│  Firewall: VM3 iptables drops all non-DB-NET traffic on :5432   │
└──────────────────────────────────────────────────────────────────┘
```

| Control | Secure Configuration |
|---------|---------------------|
| SQLi Prevention | Parameterized queries via asyncpg/psycopg3 |
| Least Privilege | `app_writer` / `app_readonly` roles per operation |
| BOLA Prevention | `WHERE account_id = ? AND user_id = ?` + RLS |
| Network Restriction | `pg_hba.conf` host record: `192.168.200.20/32` only + iptables |

---

## 5. Data Flow Diagrams

### 5.1 Normal Request Flow (Account Balance Lookup)

```
  Client Browser        VM2 FastAPI           VM3 PostgreSQL
       │                    │                       │
       │  GET /api/accounts/42                      │
       │──────────────────▶│                       │
       │                   │  Validate JWT token    │
       │                   │  Extract user_id=7     │
       │                   │                        │
       │                   │  SELECT * FROM         │
       │                   │  bank_accounts WHERE   │
       │                   │  id=$1 AND user_id=$2  │
       │                   │───────────────────────▶│
       │                   │                        │ Execute query
       │                   │                        │ Apply RLS policy
       │                   │  Result: {id:42, ...}  │
       │                   │◀───────────────────────│
       │  200 OK {balance} │                        │
       │◀──────────────────│                        │
```

### 5.2 SQL Injection Attack Flow (Vulnerable Mode)

```
  Attacker (VM1)       VM2 FastAPI             VM3 PostgreSQL
       │                    │                        │
       │  GET /api/accounts/42' OR '1'='1            │
       │──────────────────▶│                        │
       │                   │  Build query string:    │
       │                   │  "SELECT * FROM         │
       │                   │   bank_accounts WHERE   │
       │                   │   id=42' OR '1'='1"     │
       │                   │  (no sanitization)      │
       │                   │                         │
       │                   │  Injected SQL executed  │
       │                   │───────────────────────▶│
       │                   │                         │ Returns ALL rows
       │  200 OK {ALL      │  Result: all accounts   │ (injection succeeds)
       │  account data}    │◀────────────────────────│
       │◀──────────────────│                         │
```

### 5.3 BOLA Attack Flow

```
  Attacker (VM1)       VM2 FastAPI             VM3 PostgreSQL
  (Authenticated       │                        │
   as user_id=7)       │                        │
       │                    │                        │
       │  GET /api/accounts/99  (belongs to user_id=12)
       │──────────────────▶│                        │
       │                   │  Vulnerable: no         │
       │                   │  ownership check        │
       │                   │                         │
       │                   │  SELECT * FROM          │
       │                   │  bank_accounts          │
       │                   │  WHERE id=99            │
       │                   │───────────────────────▶│
       │                   │                         │ Returns row for
       │  200 OK           │  Result: account #99    │ user_id=12
       │  {another user's  │◀────────────────────────│
       │   account data}   │                         │
       │◀──────────────────│                         │
```

---

## 6. Authentication Flow

```
  Client                FastAPI                 PostgreSQL
    │                      │                        │
    │  POST /auth/login     │                        │
    │  {username, password} │                        │
    │─────────────────────▶│                        │
    │                      │                        │
    │                      │  SELECT id, hashed_pw  │
    │                      │  FROM users WHERE      │
    │                      │  username=$1           │
    │                      │───────────────────────▶│
    │                      │   {id:7, hash:"$2b.."} │
    │                      │◀───────────────────────│
    │                      │                        │
    │                      │  bcrypt.verify(        │
    │                      │    password, hash)     │
    │                      │  → True                │
    │                      │                        │
    │                      │  Generate JWT:         │
    │                      │  {sub:"7", exp:...}    │
    │                      │  Sign with SECRET_KEY  │
    │                      │                        │
    │  200 OK              │                        │
    │  {access_token: JWT} │                        │
    │◀─────────────────────│                        │
    │                      │                        │
    │  Subsequent requests: Authorization: Bearer <JWT>
    │─────────────────────▶│                        │
    │                      │  Verify JWT signature  │
    │                      │  Extract user_id=7     │
    │                      │  Inject into queries   │
    │                      │───────────────────────▶│
```

---

## 7. API Endpoint Reference

### 7.1 Authentication Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `POST` | `/auth/login` | Authenticate user, receive JWT | No |
| `POST` | `/auth/register` | Register new user | No |
| `POST` | `/auth/logout` | Invalidate session | Yes |
| `GET` | `/auth/me` | Get current user info | Yes |

### 7.2 Account Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/api/accounts` | List current user's accounts | Yes |
| `GET` | `/api/accounts/{account_id}` | Get specific account details | Yes |
| `POST` | `/api/accounts` | Create new account | Yes |
| `PUT` | `/api/accounts/{account_id}` | Update account metadata | Yes |

### 7.3 Transaction Endpoints

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/api/accounts/{account_id}/transactions` | List transactions | Yes |
| `POST` | `/api/transactions/transfer` | Transfer between accounts | Yes |
| `GET` | `/api/transactions/{tx_id}` | Get transaction detail | Yes |

### 7.4 Admin Endpoints (Privileged)

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/api/admin/users` | List all users | Yes (admin role) |
| `DELETE` | `/api/admin/users/{user_id}` | Delete user | Yes (admin role) |
| `GET` | `/api/admin/audit-log` | View audit log | Yes (admin role) |

### 7.5 Health / Status

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| `GET` | `/health` | Application health check | No |
| `GET` | `/docs` | OpenAPI documentation (dev only) | No |

---

## 8. Component Dependency Map

```
flowchart TD
    Browser[Browser / React SPA]
    Nginx[Nginx Reverse Proxy]
    FastAPI[FastAPI Application]
    PG[PostgreSQL 18.x]
    
    Browser -->|HTTP :80/:3000| Nginx
    Nginx -->|proxy_pass :8000| FastAPI
    FastAPI -->|TCP :5432| PG
    
    FastAPI --- Auth[JWT Auth Middleware]
    FastAPI --- Accounts[Account Router]
    FastAPI --- Transactions[Transaction Router]
    FastAPI --- Admin[Admin Router]
    
    PG --- Roles[DB Roles]
    PG --- RLS[Row-Level Security]
    PG --- Audit[pgaudit Logging]
```

---

*Document Owner: Infrastructure Architect | Last Updated: See version control*

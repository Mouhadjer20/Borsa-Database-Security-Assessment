# Threat Model — Borsa Security Research Platform

> **Document Version:** 1.0  
> **Framework:** STRIDE  
> **Classification:** Internal Research / Educational Use Only

---

## 1. Overview

This document presents a STRIDE threat model for the Borsa financial web application. The threat model covers the application in its **production-like** configuration (Secure Mode is the reference state; Vulnerable Mode intentionally relaxes controls for research purposes).

The STRIDE model is used to systematically identify threats across six categories: **S**poofing, **T**ampering, **R**epudiation, **I**nformation Disclosure, **D**enial of Service, and **E**levation of Privilege.

---

## 2. Assets

The following assets are identified as requiring protection:

| Asset | Description | Sensitivity |
|-------|-------------|-------------|
| **Customer Financial Data** | Account balances, transaction history, account numbers | Critical |
| **Authentication Credentials** | Passwords (hashed), JWT secrets, session tokens | Critical |
| **PostgreSQL Database** | All stored data, schema, audit logs | Critical |
| **API (FastAPI)** | Business logic, query construction, authorization checks | High |
| **Application Configuration** | `.env` files, DB connection strings, JWT secret | Critical |
| **Audit Logs** | Security event records, access logs | High |
| **Network Channels** | HTTP (app), TCP/5432 (DB), SSH (admin) | High |

---

## 3. Trust Boundaries

```
┌─────────────────────────────────────────────────────────┐
│  BOUNDARY 1: Internet / AUDIT-NET ──▶ App Server        │
│  Crossed by: HTTP requests to port 80/8000              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BOUNDARY 2: App Server ──▶ Database (DB-NET)           │
│  Crossed by: PostgreSQL connections on port 5432        │
│  Should NOT be crossed from AUDIT-NET directly          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  BOUNDARY 3: Application Tier ──▶ Database Role         │
│  Crossed by: SQL execution under a named DB role        │
│  RLS enforces row-level boundary within this crossing   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Attack Surface

| Surface | Description | Exposed To |
|---------|-------------|-----------|
| **Login Form** (`POST /auth/login`) | Username/password input | Internet / AUDIT-NET |
| **Registration Form** (`POST /auth/register`) | User account creation | Internet / AUDIT-NET |
| **Account API** (`GET /api/accounts/{id}`) | Account ID parameter | Authenticated users |
| **Transaction API** (`GET/POST /api/transactions`) | Transaction IDs, amounts | Authenticated users |
| **Admin API** (`/api/admin/*`) | Administrative operations | Admin-role users |
| **PostgreSQL Port 5432** | Direct DB access | VM2 (legitimate) + VM1 in vulnerable mode |
| **SSH Port 22** | Administrative VM access | Host machine / admin |
| **Environment Variables / .env** | Configuration secrets | Server-side processes |

---

## 5. STRIDE Threat Analysis

### 5.1 Spoofing

| Threat | Asset Targeted | Attack Vector | Likelihood (Vuln) | Likelihood (Secure) |
|--------|---------------|---------------|-------------------|---------------------|
| **Credential stuffing / brute force** | Authentication credentials | POST /auth/login with enumerated passwords | High | Low (rate limiting) |
| **JWT token forgery** | Session token | Weak JWT secret allows algorithm confusion or brute force | Medium | Low (strong secret + HS256) |
| **Username enumeration** | User existence | Timing or error message differences in login response | High | Low (generic errors) |
| **IP spoofing on DB-NET** | PostgreSQL connection | Forge source IP to bypass pg_hba.conf | Low | Very Low (iptables + pg_hba chain) |
| **DB role impersonation via SET ROLE** | DB privileges | Inject `SET ROLE` command through SQLi | High | Low (parameterized queries) |

**Mitigations (Secure Mode):**
- bcrypt password hashing with cost ≥ 12
- Strong, randomly generated JWT secret (256-bit minimum)
- Generic error messages for login failures
- Rate limiting on `/auth/login`
- pg_hba.conf restricts DB connections by IP and role name

---

### 5.2 Tampering

| Threat | Asset Targeted | Attack Vector | Likelihood (Vuln) | Likelihood (Secure) |
|--------|---------------|---------------|-------------------|---------------------|
| **SQL Injection — data modification** | Financial data | Malicious input in URL/body → UPDATE/DELETE via injected SQL | High | Very Low (parameterized) |
| **SQL Injection — schema modification** | Database schema | Injected DDL (DROP TABLE, ALTER) if role has DDL privileges | High | Very Low (least privilege + params) |
| **BOLA — unauthorized account update** | Another user's account | Manipulate account_id in PUT request | High | Low (ownership check + RLS) |
| **JWT tampering** | Session claims | Modify user_id claim in JWT payload | Low | Very Low (signature verification) |
| **Audit log tampering** | Audit log integrity | Write to security_audit table if role has INSERT | Medium | Low (auditor role read-only for app) |
| **pg_hba.conf modification** | Network access control | Requires OS-level access to VM3 | Low | Low (OS hardening required) |

**Mitigations (Secure Mode):**
- Parameterized queries prevent SQL injection entirely
- `app_writer` role lacks DDL privileges
- Ownership check (`WHERE user_id = $current_user_id`) in all account queries
- RLS as independent DB-level enforcement
- Audit log table: app role has INSERT only; no UPDATE or DELETE

---

### 5.3 Repudiation

| Threat | Asset Targeted | Attack Vector | Likelihood (Vuln) | Likelihood (Secure) |
|--------|---------------|---------------|-------------------|---------------------|
| **Login attempts not logged** | Audit trail | No authentication event logging | High | Low (application + pgaudit logging) |
| **DB query history not captured** | Query audit | No `log_statement` or pgaudit configuration | High | Low (pgaudit enabled) |
| **Transaction disputes** | Financial data | No immutable transaction log | Medium | Low (transaction table + DB triggers) |
| **Admin actions not attributed** | Admin audit trail | Admin API calls not logged with user identity | Medium | Low (structured logging with JWT subject) |

**Mitigations (Secure Mode):**
- pgaudit extension enabled on VM3 with `log_statement = 'all'` for sensitive roles
- Application-level structured logging (JSON) with user_id in every log line
- Transactions table is append-only (no DELETE privilege for app role)
- `security_audit` table records authentication events

---

### 5.4 Information Disclosure

| Threat | Asset Targeted | Attack Vector | Likelihood (Vuln) | Likelihood (Secure) |
|--------|---------------|---------------|-------------------|---------------------|
| **SQL Injection — data exfiltration** | Customer financial data | UNION-based or error-based SQLi dumps table data | High | Very Low (parameterized) |
| **BOLA — cross-customer data access** | Account data | account_id manipulation returns another user's records | High | Low (ownership check + RLS) |
| **Verbose DB error messages** | Schema information | PostgreSQL error messages expose table/column names | High | Low (generic error handling) |
| **Direct DB connection from AUDIT-NET** | All database content | psql direct connect from Kali if port exposed | High | Very Low (firewall + pg_hba) |
| **Environment variable exposure** | DB credentials, JWT secret | .env file readable by web server process | Medium | Low (file permissions, secrets mgmt) |
| **pg_shadow access** | Password hashes | SUPERUSER role can read hashed passwords | High | Very Low (no SUPERUSER for app) |
| **Information in HTTP headers** | Server fingerprint | Server: uvicorn header reveals technology stack | Low | Low (can be suppressed in Nginx) |

**Mitigations (Secure Mode):**
- Parameterized queries + RLS + ownership checks (defense-in-depth for data access)
- Generic error messages in production mode (`DEBUG=false`)
- Firewall drops port 5432 traffic from non-DB-NET sources
- pg_hba.conf: `192.168.200.20/32` only
- `.env` files: `chmod 600`, owned by app service user
- App role: no SUPERUSER, no pg_shadow access

---

### 5.5 Denial of Service

| Threat | Asset Targeted | Attack Vector | Likelihood (Vuln) | Likelihood (Secure) |
|--------|---------------|---------------|-------------------|---------------------|
| **Login endpoint flooding** | App Server availability | High-volume POST /auth/login requests | High | Medium (rate limiting + connection pool limits) |
| **Expensive SQL queries** | DB Server CPU | Time-based blind SQLi with SLEEP-equivalent queries | High | Low (parameterized queries + query timeout) |
| **Connection pool exhaustion** | DB connections | Many concurrent unauthenticated requests holding connections | Medium | Low (pool limits, connection timeout) |
| **Large payload attacks** | App server memory | Oversized JSON bodies | Medium | Low (body size limit in Nginx/FastAPI) |

**Mitigations (Secure Mode):**
- Rate limiting on authentication endpoints
- `statement_timeout` set in PostgreSQL (`postgresql.conf`)
- DB connection pool size limits (asyncpg pool max_size)
- Nginx `client_max_body_size` limit

---

### 5.6 Elevation of Privilege

| Threat | Asset Targeted | Attack Vector | Likelihood (Vuln) | Likelihood (Secure) |
|--------|---------------|---------------|-------------------|---------------------|
| **SQLi → SUPERUSER operations** | Database admin | Injected `SET ROLE postgres` or DDL via app_vulnerable | High | Very Low (parameterized + least priv) |
| **app_vulnerable role DDL abuse** | Database schema | App role has DROP/CREATE privileges | High | Very Low (app_writer lacks DDL) |
| **Horizontal privilege escalation (BOLA)** | Other users' data | account_id manipulation to access other accounts | High | Low (ownership check + RLS) |
| **Admin API access without admin role** | Admin functions | No role check on /api/admin/* endpoints | Medium | Low (role-based access control in middleware) |
| **pg_hba.conf any/trust auth** | DB authentication | trust auth method bypasses password entirely | High | Very Low (scram-sha-256 method required) |

**Mitigations (Secure Mode):**
- `app_writer` role: no DDL, no SUPERUSER, no pg_shadow
- `app_readonly` role: SELECT only on specific tables
- Authorization middleware checks `is_admin` claim in JWT for admin endpoints
- pg_hba.conf: `scram-sha-256` method for all application roles

---

## 6. Risk Ratings

Risk ratings are provided for the **Vulnerable Mode** state (before controls are applied).

| Threat | CVSS 4.0 Vector (approx.) | Base Score | Rating |
|--------|--------------------------|-----------|--------|
| SQLi — data exfiltration | AV:N/AC:L/AT:N/PR:N/UI:N — VC:H/VI:H/VA:N/SC:H/SI:H/SA:N | 9.3 | **Critical** |
| SQLi — schema modification | AV:N/AC:L/AT:N/PR:L/UI:N — VC:H/VI:H/VA:H/SC:H/SI:H/SA:H | 9.4 | **Critical** |
| Excessive privileges (DDL abuse) | AV:N/AC:L/AT:N/PR:L/UI:N — VC:H/VI:H/VA:H/SC:N/SI:N/SA:N | 8.7 | **High** |
| BOLA — cross-account access | AV:N/AC:L/AT:N/PR:L/UI:N — VC:H/VI:L/VA:N/SC:N/SI:N/SA:N | 7.1 | **High** |
| DB network exposure | AV:N/AC:L/AT:N/PR:N/UI:N — VC:H/VI:H/VA:H/SC:H/SI:H/SA:H | 9.4 | **Critical** |
| JWT brute force | AV:N/AC:H/AT:N/PR:N/UI:N — VC:H/VI:H/VA:N/SC:H/SI:H/SA:N | 8.1 | **High** |

> **Note:** CVSS 4.0 scores above are illustrative for pedagogical purposes. Scores must be validated against the actual CVSS 4.0 calculator using precise metric selections for each experiment.

---

## 7. Intentional Exposures in Lab Mode

The following weaknesses are **deliberately introduced** in Vulnerable Mode for research purposes. They must never appear in production systems.

| Exposure | Purpose | How Introduced |
|----------|---------|----------------|
| String-concatenated SQL queries | Demonstrate CWE-89 | `QUERY_MODE=vulnerable` env var |
| `app_vulnerable` SUPERUSER role | Demonstrate CWE-250 | Separate DB role with broad grants |
| Missing ownership check on account API | Demonstrate CWE-284 | `AUTHZ_MODE=disabled` env var |
| `pg_hba.conf` allowing AUDIT-NET | Demonstrate CWE-668 | Swappable pg_hba config file |
| Verbose error messages | Make attacks observable | `DEBUG=true` env var |

> **⚠️ WARNING:** Never deploy Vulnerable Mode configuration outside the VirtualBox lab. These configurations represent serious security defects that would result in immediate compromise in a production environment.

---

## 8. Mitigations in Secure Mode — Summary

| Control | Mitigates | Implementation |
|---------|-----------|---------------|
| Parameterized queries | CWE-89 (SQLi) | asyncpg/psycopg3 `$1, $2` syntax |
| Least-privilege DB roles | CWE-250 | `app_readonly`, `app_writer` with minimal GRANT |
| Ownership check in queries | CWE-284 (BOLA) | `WHERE user_id = $current_user` |
| PostgreSQL RLS policies | CWE-284 (defense-in-depth) | `CREATE POLICY` on bank_accounts, transactions |
| Firewall rules (iptables) | CWE-668 | Drop port 5432 from non-DB-NET on VM3 |
| pg_hba.conf restriction | CWE-668 | `host borsa app_writer 192.168.200.20/32 scram-sha-256` |
| bcrypt password hashing | Spoofing | bcrypt cost ≥ 12 |
| JWT strong secret | JWT tampering | 256-bit random secret |
| Generic error messages | Information disclosure | `DEBUG=false` |
| Rate limiting | DoS / brute force | Slowapi or Nginx `limit_req` |
| pgaudit logging | Repudiation | pgaudit extension + log_statement |

---

*Document Owner: Security Analyst | Last Updated: See version control*

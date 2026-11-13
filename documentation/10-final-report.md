# 10 — Final Security Assessment & Research Report

## Executive Summary
This report summarizes the security assessment conducted on **Borsa**, an educational financial web application and database security research platform. The evaluation examined the effectiveness of layered defensive controls against four primary threat scenarios: SQL Injection, Excessive Database Privileges, Broken Object-Level Authorization, and Database Network Exposure.

The assessment was executed as a black-box CTF within an isolated VirtualBox laboratory using synthetic financial data. The vulnerabilities were embedded directly into legitimate-looking application endpoints to simulate real-world web application penetration testing.

---

## Key Findings & Vulnerability Verification

### 1. SQL Injection (CWE-89)
- **Vulnerable Surface:** `GET /api/auth/search?q=` (User directory search tool).
- **Vulnerability Mechanism:** Dynamic string formatting in user lookup query: `f"SELECT ... WHERE username LIKE '%{q}%'"`.
- **Exploitation Impact:** Authentication bypass via `' OR '1'='1` and full exfiltration of password hashes from `app_users` table via `UNION SELECT` (CVSS 4.0: 8.7 High).
- **Remediation:** Parameterized queries and SQLAlchemy bind parameters eliminate query injection completely.

### 2. Excessive Database Privileges (CWE-250)
- **Vulnerable Surface:** `GET /api/transactions/export` (Transaction export tool).
- **Vulnerability Mechanism:** Inclusion of internal database diagnostic data (`current_user`, `session_user`, `pg_backend_pid`, `version()`) in API response metadata.
- **Exploitation Impact:** Discloses internal database identities and version information, enabling targeted exploitation of database catalogs via SQLi (CVSS 4.0: 7.2 High).
- **Remediation:** Restricting application identities to least-privileged roles (`app_readonly` / `app_writer`) and stripping debug metadata from public endpoints.

### 3. Broken Object-Level Authorization (CWE-284)
- **Vulnerable Surface:** `GET /api/accounts/lookup/{account_ref}` (Account reference verification).
- **Vulnerability Mechanism:** Missing customer identity validation (`customer_id` check) in database query.
- **Exploitation Impact:** Horizontal privilege escalation allowing any authenticated customer to view balances and account details of all other bank customers (CVSS 4.0: 7.5 High).
- **Remediation:** Enforce application-layer ownership checks (`customer_id == current_user.customer_id`) and PostgreSQL Row-Level Security (RLS) as a database-tier fallback.

### 4. Database Network Exposure & SSRF (CWE-668)
- **Vulnerable Surface:** `GET /api/diagnostics/db-ping?host=&port=` (Database connectivity tool).
- **Vulnerability Mechanism:** Unrestricted network socket probe allowing user-specified host and port inputs.
- **Exploitation Impact:** Adversaries can pivot from the application tier to map internal non-routable network ranges (DB-NET) and probe internal localhost services (CVSS 4.0: 7.5 High).
- **Remediation:** Strict allowlisting of probe targets to the configured database host/port only, coupled with egress filtering.

---

## Defensive Recommendations & Best Practices

1. **Always use parameterized statements or ORM binding.** Never concatenate untrusted user input into SQL commands.
2. **Implement PostgreSQL Row-Level Security (RLS)** as a defense-in-depth safeguard against application-level authorization omissions.
3. **Enforce least-privilege database role separation.** Maintain separate `app_readonly` and `app_writer` roles; never grant DDL or superuser privileges to the web tier.
4. **Isolate database servers on dedicated, non-routable internal subnets** with strict host firewall configurations (UFW allowing port 5432 only to the application server IP).
5. **Validate all input against strict allowlists** on any internal diagnostic or network-probing utility to prevent SSRF and internal pivoting.

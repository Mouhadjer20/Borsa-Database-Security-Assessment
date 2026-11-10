# 10 — Final Security Assessment & Research Report

## Executive Summary
This report summarizes the security assessment conducted on **Borsa**, an educational financial web application and database security research platform. The evaluation examined the effectiveness of layered defensive controls against four primary threat scenarios: SQL Injection, Excessive Database Privileges, Broken Object-Level Authorization, and Database Network Exposure.

Testing was performed within an isolated three-VM VirtualBox laboratory using synthetic financial records.

---

## Key Findings

### 1. SQL Injection (CWE-89)
- **Vulnerable Variant (A):** Direct string formatting permitted full query manipulation and authentication bypass (CVSS 4.0: 8.7 High).
- **Remediation (B):** Parameterized queries and SQLAlchemy bind parameters eliminated the vulnerability.

### 2. Excessive Database Privileges (CWE-250)
- **Vulnerable Variant (A):** Use of an overprivileged database account allowed querying system tables and administrative data (CVSS 4.0: 7.2 High).
- **Remediation (B):** Restricting application identities to `app_readonly` and `app_writer` successfully enforced least-privilege boundaries.

### 3. Broken Object-Level Authorization (CWE-284)
- **Vulnerable Variant (A):** Inadequate ownership checks enabled horizontal privilege escalation across customer accounts (CVSS 4.0: 7.5 High).
- **Remediation (B & C):** Server-side customer_id validation and PostgreSQL Row-Level Security (RLS) successfully isolated multi-tenant records.

### 4. Database Network Exposure (CWE-668)
- **Vulnerable Variant (B):** Permitting external subnets to connect directly to PostgreSQL exposed the database service to unauthorized network reconnaissance.
- **Remediation (A):** Restricting PostgreSQL listener addresses to `192.168.200.30` and enforcing host firewall rules completely isolated the database tier.

---

## Recommendations & Best Practices
1. **Never construct dynamic SQL using string concatenation.** Always use parameterized queries or ORM expressions.
2. **Implement PostgreSQL Row-Level Security (RLS)** as a defense-in-depth safeguard against application-level authorization omissions.
3. **Enforce strict database role separation.** Never use superuser accounts or broad grants for runtime web applications.
4. **Isolate database servers on dedicated, non-routable internal subnets** with strict host firewall configurations.


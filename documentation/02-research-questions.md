# Research Questions — Borsa Security Research Platform

> **Document Version:** 1.0  
> **Linked Charter:** `01-project-charter.md`  
> **Classification:** Internal Research / Educational Use Only

---

## Overview

This document defines the structured research questions that guide the Borsa security research project. Each primary research question corresponds to one experimental security scenario and is supported by secondary (sub-) questions that probe deeper aspects of the vulnerability and its mitigations.

Research questions are designed to be **empirically answerable** through controlled experiments in the VirtualBox lab environment.

---

## Primary Research Questions

### RQ1 — SQL Injection (CWE-89)

> **Can SQL injection be used to manipulate the Borsa application's database queries, and does parameterized query construction effectively eliminate this attack vector?**

This question investigates whether an unauthenticated or authenticated attacker can craft malicious HTTP input that alters the structure of SQL queries executed by the FastAPI backend, resulting in unauthorized data access, authentication bypass, or data exfiltration. The comparative component asks whether switching to parameterized queries demonstrably prevents all tested injection payloads.

**Hypothesis:** String-concatenated query construction will be exploitable via standard injection payloads, while parameterized queries will reject all tested payloads without application changes.

---

### RQ2 — Excessive Database Privileges (CWE-250)

> **Does the database role used by the Borsa application hold excessive PostgreSQL privileges, and can those excess privileges be exploited to perform operations beyond the application's intended function?**

This question investigates whether the principle of least privilege is enforced at the PostgreSQL role level. It tests whether an attacker who achieves code execution on VM2 (App Server) or who can inject SQL (Scenario 1) can leverage excessive role privileges to perform destructive or unauthorized database operations — such as dropping tables, reading system catalogs, or writing to audit logs.

**Hypothesis:** An overprivileged role (e.g., `app_vulnerable` with SUPERUSER or broad GRANT) will allow operations that a least-privilege role (`app_readonly`, `app_writer`) will reject with a PostgreSQL permission error.

---

### RQ3 — Broken Object Level Authorization / BOLA (CWE-284)

> **Can an authenticated user of the Borsa application access or modify the financial account data of another user, and do application-level and database-level (RLS) authorization controls independently prevent this?**

This question investigates whether the API enforces ownership checks before returning sensitive financial data. BOLA (Broken Object Level Authorization), also known as IDOR (Insecure Direct Object Reference), occurs when an API accepts a user-supplied resource identifier (e.g., `account_id`) without verifying that the requesting user owns that resource. The question further probes whether PostgreSQL Row-Level Security (RLS) provides an independent, database-enforced backstop even when the application-level check fails.

**Hypothesis:** Without authorization checks, manipulating the `account_id` in an API request will return another customer's financial data. Application-level checks and PostgreSQL RLS will independently and together prevent this, with RLS providing defense-in-depth that persists even if application-layer checks are bypassed.

---

### RQ4 — Database Network Exposure (CWE-668)

> **Is the PostgreSQL database server on VM3 reachable from the AUDIT-NET network segment (192.168.100.0/24), and do firewall rules and pg_hba.conf configuration reliably restrict access to only the authorized DB-NET segment (192.168.200.0/24)?**

This question investigates whether the database server is exposed to unauthorized network segments. In a properly segmented architecture, VM3 should be reachable only from VM2 (the App Server) via DB-NET. This scenario tests whether a Kali Linux attacker on AUDIT-NET can reach port 5432 on VM3 directly, bypassing the application tier entirely.

**Hypothesis:** In the vulnerable configuration (permissive `pg_hba.conf`, no firewall), an attacker on AUDIT-NET will be able to connect to PostgreSQL on VM3 directly. In the secure configuration (restrictive firewall + `pg_hba.conf`), all connection attempts from AUDIT-NET will be dropped at the network layer before reaching PostgreSQL.

---

## Secondary Research Questions

### SQLi Secondary Questions

| ID | Question |
|----|----------|
| RQ1a | Which categories of SQLi payloads (classic, UNION-based, boolean-blind, time-based) succeed in the vulnerable variant? |
| RQ1b | Does `sqlmap` automated detection confirm the same vulnerability that manual testing identifies? |
| RQ1c | What error messages or behavioral differences are observable to an attacker in each variant? |
| RQ1d | Can SQLi be used to extract credentials or schema information, not just query data? |

### Excessive Privileges Secondary Questions

| ID | Question |
|----|----------|
| RQ2a | What is the minimum set of PostgreSQL privileges required for the Borsa application to function correctly? |
| RQ2b | Can audit log evidence (pgaudit or PostgreSQL logs) detect privilege escalation attempts? |
| RQ2c | Does the `app_vulnerable` role's excess privilege allow reading `pg_shadow` (password hashes)? |
| RQ2d | How does PostgreSQL respond to privilege-denied operations — does it expose schema information in error messages? |

### BOLA/RLS Secondary Questions

| ID | Question |
|----|----------|
| RQ3a | Is the BOLA vulnerability exploitable without authentication, or only by an authenticated user? |
| RQ3b | Does PostgreSQL RLS prevent data leakage even when the query reaches the database with a valid session? |
| RQ3c | Can RLS policies be configured without breaking legitimate application functionality? |
| RQ3d | What is the performance impact (if any) of enabling RLS on the `bank_accounts` and `transactions` tables? |
| RQ3e | Does the RLS policy remain effective when the `app_vulnerable` role (with broad privileges) is used? |

### Network Exposure Secondary Questions

| ID | Question |
|----|----------|
| RQ4a | What information does an `nmap` scan of VM3 reveal from the AUDIT-NET perspective (open ports, service version, OS)? |
| RQ4b | Is it possible to authenticate to PostgreSQL from Kali (AUDIT-NET) if `pg_hba.conf` permits it? |
| RQ4c | Does the firewall block the connection before `pg_hba.conf` is consulted, or does the connection reach PostgreSQL? |
| RQ4d | Does restricting `listen_addresses` in `postgresql.conf` provide an additional layer of protection? |

---

## Vulnerability Chaining Research Questions

| ID | Question |
|----|----------|
| RQC1 | Can SQL injection (RQ1) be combined with excessive privileges (RQ2) to escalate impact beyond what either vulnerability alone allows? |
| RQC2 | Does fixing one vulnerability in the chain (e.g., parameterized queries) break the entire attack chain, or can the attacker pivot? |
| RQC3 | Does network segmentation (RQ4) limit the blast radius of a successful SQLi + privilege escalation attack? |

---

## Defense Effectiveness Research Questions

| ID | Question |
|----|----------|
| RQD1 | Do all four secure-mode controls together eliminate all identified attack vectors, or do residual risks remain? |
| RQD2 | Is defense-in-depth (layered controls) measurably more effective than any single control applied in isolation? |
| RQD3 | What is the implementation complexity cost of each security control, and how does it compare to the risk reduction achieved? |

---

## Measurement Approach

Each research question will be answered using the following evidence types:

| Evidence Type | Description |
|---------------|-------------|
| **Command output** | Terminal output from `psql`, `curl`, `nmap`, `sqlmap` showing attack success/failure |
| **HTTP responses** | API response bodies demonstrating data returned or errors raised |
| **PostgreSQL logs** | Log entries confirming query execution, errors, or access denials |
| **Screenshots** | Visual evidence of UI behavior and tool output |
| **CVSS 4.0 score** | Quantitative risk rating for vulnerable state of each scenario |

Results are recorded in `documentation/09-results-and-analysis.md`.

---

*Document Owner: Principal Researcher | Last Updated: See version control*

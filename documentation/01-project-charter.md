# 01 — Project Charter

| Field | Value |
|---|---|
| Project | BorsaTrust — Database Security Assessment |
| Version | 1.0 (draft) |
| Date | 2026-11-06 |
| Domain | Fictional banking and financial services (lab only) |
| DBMS | PostgreSQL 18.x (latest supported minor at implementation) |
| Application | FastAPI (Python), REST API, Uvicorn, Psycopg 3, SQLAlchemy 2 + controlled direct SQL |

## Purpose

Conduct a controlled security assessment of a small banking platform, implement defensive controls, and experimentally verify their effectiveness. The project treats database security as a research problem: distinguish **vulnerability**, **attack technique**, **observed impact**, and **security control**, then test whether controls reduce or eliminate the observed behavior.

## Research Scenario

**BorsaTrust** is a fictional financial institution managing synthetic customer accounts, transactions, employees, and internal banking operations. All identities, account numbers, balances, and transactions are artificial. No real banking data, payment systems, or external institutions are involved.

## Objectives

1. Demonstrate and measure four controlled security weaknesses in a relational database-backed application.
2. Map findings to CWE/CAPEC, MITRE ATT&CK (where behavior matches), and CVSS v4.0.
3. Implement layered defenses and retest with identical test cases.
4. Compare pre/post-defense results quantitatively and qualitatively.
5. Evaluate PostgreSQL security mechanisms (roles/privileges, RLS, listener/auth config, auditing) under controlled conditions.

## Primary Scenarios

1. SQL Injection
2. Excessive Database Privileges
3. Broken Authorization
4. Database Network Exposure

## Research Extensions (time permitting)

- PostgreSQL Row-Level Security vs. application authorization
- Vulnerability chaining / defense-in-depth analysis
- Database auditing and detection coverage
- Quantitative comparison of defensive controls

## Deliverables

- Research design and threat model documentation
- Isolated 3-VM lab (Kali, application, PostgreSQL)
- Vulnerable and secured application implementations (separated)
- Attack procedures, evidence, and logs
- Findings with CWE/ATT&CK/CVSS v4.0, remediation, and retest outcomes
- Comparative results matrix and final report

## Constraints

- Lab-only, isolated networks; no internet/bridged access during experiments.
- Vulnerable code/configuration runs only inside the lab; snapshots before each experiment.
- Supported PostgreSQL release; vulnerabilities introduced deliberately in application/configuration, not by using an outdated DBMS.
- Reproducibility: record exact versions, configs, topology, test accounts, and test cases.

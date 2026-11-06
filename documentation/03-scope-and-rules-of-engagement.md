# 03 — Scope and Rules of Engagement

## Scope

### In Scope

- BorsaTrust fictional banking application (REST API) and its PostgreSQL 18.x database.
- Three dedicated VMs: Kali (auditor), application server, database server.
- Isolated AUDIT-NET and DB-NET zones; optional MGMT-NET for host administration only.
- Controlled scenarios: SQL injection, excessive DB privileges, broken authorization, database network exposure.
- Defensive controls: parameterized queries, least privilege, application/DB authorization (including RLS extension), network segmentation, listener/auth restrictions, TLS (as applicable), auditing.
- Evidence collection, CWE/CAPEC/ATT&CK mapping (when behavior matches), CVSS v4.0 scoring, retesting.

### Out of Scope

- Real banking systems, real customer data, payment processors, or external networks.
- Attacks against hosts/services not part of the lab.
- Social engineering, phishing, physical access, or denial-of-service against non-lab infrastructure.
- Using outdated/vulnerable DBMS releases to manufacture findings.
- Production deployment of the vulnerable application.

## Rules of Engagement

1. **Authorization:** All testing is performed only against assets owned/controlled for this lab.
2. **Isolation:** No internet or bridged access during experiments. Default policy: Kali→App permitted; App→DB permitted on required DB port; Kali→DB denied.
3. **Change control:** Every deliberate weakness, config change, and remediation is documented (what, why, when, before/after state). Network-exposure rule changes are temporary and restored after testing.
4. **Safety:** Use synthetic data and canary records. Do not collect unnecessary sensitive information. Keep vulnerable and secured implementations separated.
5. **Reproducibility:** Snapshot VMs before experiments. Record exact OS/kernel, PostgreSQL major/minor, Python/framework/driver versions, extensions, config files, topology, and test identities.
6. **Evidence integrity:** Preserve logs/screenshots/captures with timestamps and test-case IDs. Do not alter evidence after collection except for documented redaction of accidental non-lab data (not expected).
7. **Retesting discipline:** Use identical test cases, accounts, data, and initial conditions for pre- and post-defense comparisons.
8. **Identity separation:** Never use PostgreSQL superuser as the normal application connection. Distinguish application users from PostgreSQL roles.

## Test Accounts (planned)

| Identity | Purpose |
|---|---|
| `db_owner` | Controlled object ownership/administration |
| `app_readonly` | Read-only application operations |
| `app_writer` | Limited application write operations |
| `app_vulnerable` | Deliberately overprivileged experimental account |
| `auditor` | Authorized security inspection |
| `migration_role` | Controlled schema migrations |

Synthetic application users: Customer A/B/C, Employee D, Administrator E (explicit permissions). Canary records provide unambiguous unauthorized-access indicators.

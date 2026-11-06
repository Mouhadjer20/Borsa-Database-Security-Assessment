# 04 — Architecture

## Logical Lab Topology

| VM | Role | Network Interfaces | Key Components |
|---|---|---|---|
| VM 1 — Kali Linux | Auditor workstation | AUDIT-NET | Nmap, Burp Suite, SQLmap, Wireshark, `psql` |
| VM 2 — Application Server | Dual-homed app tier | AUDIT-NET + DB-NET | Linux, Python, FastAPI, Uvicorn/Gunicorn, app logs |
| VM 3 — Database Server | Protected data tier | DB-NET only | Linux, PostgreSQL 18.x, roles, RLS, audit logs, synthetic data |

## Network Zones

| Zone | Members | Purpose |
|---|---|---|
| AUDIT-NET | Kali + App VM | Application assessment |
| DB-NET | App VM + DB VM | Database communication |
| MGMT-NET (optional) | Host/admin only | Administrative access; not used as attack path |

**Default policy**
- Kali → Application: permitted (required test traffic only).
- Application → PostgreSQL: permitted on required DB port.
- Kali → PostgreSQL: denied.
- Internet/bridged: disabled during experiments.
- App VM is dual-homed but must not act as an unrestricted router.

## Trust Boundaries

1. **User → Application:** authentication, input handling, API authorization.
2. **Application → Database:** DB identity, least privilege, query construction, session context.
3. **External client → Database network:** segmentation, firewall, listener exposure, client auth rules.

A key property of this design: network restriction (Kali cannot reach DB directly) does **not** prevent SQL injection through the legitimate application path. Controls are evaluated per boundary.

## PostgreSQL Security-Relevant Components

| Component | Security relevance |
|---|---|
| Client interface / auth subsystem | Entry point; authentication methods and client rules |
| Server process / session role | SQL executes under a database role (process-per-connection model) |
| Role system & privileges | RBAC, least privilege, ownership |
| Schema/object permissions | Database/schema/table/sequence/function/column controls |
| Row-Level Security | Row access policies; compared to application authorization |
| Query processor | Relevant to SQL injection impact on query semantics |
| WAL / catalogs | Durability, metadata (roles, permissions, objects) |
| Logging/auditing | Detection and investigation evidence |

## Defensive Layers (planned)

- **Application:** parameterized queries/prepared statements, server-side authorization, safe DB access patterns, input validation as supplement.
- **Database:** role separation, explicit GRANT/REVOKE, restricted ownership, migration/runtime separation, RLS (extension), logging.
- **Network/transport:** segmentation, host firewall, PostgreSQL `listen_addresses`/client auth restrictions, TLS for DB connections (as applicable).

## Reproducibility Checklist

Record before experiments: exact PostgreSQL major/minor, OS/kernel, Python/FastAPI/Uvicorn/Psycopg/SQLAlchemy versions, extensions, relevant config files, VM specs, network topology, firewall rules, test accounts, seed data version, and snapshots.

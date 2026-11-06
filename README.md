# Borsa — Database Security Assessment

Controlled security assessment of a fictional financial information system, with defensive controls and experimental verification.

## Research Focus

Borsa is a lab-only financial platform scenario (synthetic data) used to study:

- SQL injection (unsafe query construction vs. parameterized queries)
- Excessive database privileges (overprivileged identity vs. least privilege)
- Broken authorization (missing object checks vs. application/DB enforcement)
- Database network exposure (segmented access vs. exposed service)

Each finding is documented with root cause, observed impact, evidence, CWE/CAPEC/ATT&CK mapping (where applicable), CVSS v4.0 scoring, remediation, and retest results.

## Scope & Safety

- **Fictional environment only.** No real banking data, payment systems, or external institutions.
- **Isolated lab.** Experiments run in dedicated VMs with documented network boundaries.
- Vulnerable configurations are kept separate from secured implementations and are not intended for production use.

## Planned Architecture

- **Audit workstation:** Kali Linux
- **Application server:** Linux, Python, FastAPI, Uvicorn
- **Database server:** PostgreSQL 18.x (supported minor release), roles/RLS/audit logging
- **Topology:** segmented audit and database network zones; DB access restricted to the application server by default.

## Repository Layout

- `documentation/` — charter, research questions, scope/RoE, architecture, threat model, methodology, final report
- `infrastructure/` — VM specs, network topology, firewall, database configuration
- `database/` — schema, seed data, roles, policies (incl. RLS), audit
- `application/` — `vulnerable/` and `secured/` implementations + tests
- `attacks/` — scenario procedures and observations
- `defense/` — implemented controls
- `verification/` — pre/post-defense and regression tests
- `evidence/` — curated screenshots/logs/captures
- `reporting/` — findings, CVSS vectors, ATT&CK/CWE mappings, comparative results
- `references/` — standards and bibliography

## Status

Initialized repository structure. Next milestone: **Research Design Document v1.0** (see `project_prompt.md` in `references/`).

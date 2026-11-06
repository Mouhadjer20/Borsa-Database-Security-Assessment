# 05 — Threat Model

## Assets

| Asset | Security property | Example impact |
|---|---|---|
| Customer records (PII, synthetic) | Confidentiality | Unauthorized disclosure |
| Account identifiers/balances | Confidentiality, Integrity | Disclosure; unauthorized modification |
| Transaction histories | Integrity, Confidentiality | Manipulation; unauthorized access |
| Employee/administrator accounts | Confidentiality, Integrity | Unauthorized access |
| Application DB credentials/roles | Confidentiality, Integrity | Privilege abuse |
| Audit/security logs | Integrity, Accountability | Evidence loss or concealment |
| Banking services (API/DB availability) | Availability | Service disruption |

## Actors (lab)

| Actor | Description |
|---|---|
| Unauthenticated external tester | Reaches application via AUDIT-NET (Kali) |
| Authenticated low-privilege customer | Legitimate app user attempting cross-customer access |
| Compromised application DB identity | App-to-DB role after application weakness or misconfiguration |
| Authorized auditor/admin | Controlled inspection; baseline for expected access |
| Misconfigured network/firewall state | Experimental condition for exposure scenario |

## Entry Points and Attack Surface

- REST API endpoints exposed to AUDIT-NET (input handling, authn/authz, DB queries).
- Application database connection to PostgreSQL on DB-NET.
- PostgreSQL listener/client authentication surface (should be restricted to App VM by default).
- Database roles, privileges, ownership, RLS policies, and functions (e.g., `SECURITY DEFINER` risks as extension).
- Configuration: app query construction, DB grants, `pg_hba`/listener settings, host firewall rules.

## Scenario Threat Statements

| ID | Threat | Primary weakness | Expected impact (if confirmed) |
|---|---|---|---|
| T-SQLi | Input alters intended SQL behavior | CWE-89, unsafe query construction | Unauthorized read/modify of financial records (observed scope only) |
| T-PRIV | App DB identity can perform excess operations | CWE-250 / excessive privileges | Unauthorized DB operations beyond app responsibility |
| T-AUTHZ | User accesses another customer's resources | CWE-862/863, broken object authorization | Cross-customer disclosure/modification |
| T-NET | DB accepts connections from unauthorized network location | CWE-668 or specific misconfiguration | Increased access paths; unauthorized connection attempts/success per config |

## ATT&CK/CWE/CAPEC Mapping Guidance

- Use **CWE** for weakness classification, **CAPEC** for attack patterns where helpful, **MITRE ATT&CK** only when simulated behavior matches the technique.
- Document: tactic, technique ID/name (if applicable), adversary objective, observed lab behavior, evidence, detection opportunity, mitigation.
- Do not force mappings. Broken authorization may map to valid-account misuse or data-from-databases collection only when those behaviors are actually observed.

## Assumptions

- Lab assets are controlled and isolated.
- Synthetic data and canary records are used.
- Vulnerable states are intentionally introduced and documented.
- PostgreSQL runs on a supported 18.x release.

## Out of Model

- Internet-facing exploitation, real-world threat actors, phishing, physical compromise, non-lab hosts, and availability attacks outside controlled measurements.

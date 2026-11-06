# 07 — Methodology

## Approach

Controlled before-and-after experimental design aligned with NIST SP 800-115 (technical security testing) and OWASP WSTG (web testing). Findings are classified with CWE/CAPEC, mapped to MITRE ATT&CK only when behavior matches, and scored with CVSS v4.0.

## Lifecycle

| Phase | Activities | Outputs |
|---|---|---|
| 0. Preparation | Scope, assets, hypotheses, threat model, boundaries, test accounts | Charter, RQs, scope/RoE, threat model |
| 1. Baseline | Deploy lab, document initial config, confirm expected behavior | Architecture/config baseline, snapshots |
| 2. Vulnerability introduction | Introduce controlled app/config weaknesses (documented) | Vulnerable variant, change log |
| 3. Assessment | Recon, scanning, vulnerability identification, controlled exploitation | Test execution records |
| 4. Evidence collection | App/DB logs, network observations, screenshots, results | Evidence package per test case |
| 5. Defensive implementation | Apply controls; document every modification | Secured variant, remediation notes |
| 6. Retesting | Repeat identical test cases | Post-defense results |
| 7. Comparative analysis | Compare states, evaluate hypotheses, risk/CVSS | Results matrix, analysis |
| 8. Reporting | Findings, mappings, scores, recommendations | Final report |

## Test Case Template

Each test case records: `TC-ID`, scenario, objective, preconditions, accounts/data, steps (high level), expected vulnerable result, expected secured result, evidence collected, actual result, pass/fail, and notes. Identical test cases are reused for pre/post comparison.

## Scenario Matrix

| Scenario | Vulnerable variant | Secured variant(s) | Key metrics |
|---|---|---|---|
| SQL Injection | Unsafe SQL construction | Parameterized queries; restricted DB identity; validation as supplement | Query semantics manipulated? records accessed/modified, logs, retest outcome |
| Excessive Privileges | `app_vulnerable` overprivileged | Least-privilege roles; explicit GRANT/REVOKE; runtime/migration separation | Permitted ops count, unauthorized ops attempted/succeeded |
| Broken Authorization | Missing/incorrect ownership checks | Correct server-side checks; PostgreSQL RLS (extension) | Cross-customer attempts, records returned/modified, enforcement layer |
| Network Exposure | DB exposed to AUDIT-NET (temporary, documented) | Segmentation, firewall, listener/client-auth restrictions, TLS | Port/connection success-failure, source, auth outcome |

## Vulnerability Chaining (extension)

After individual scenarios, evaluate combined conditions (e.g., application weakness + excessive DB privilege). Assess each finding independently; explain chain/business impact separately. Do **not** add CVSS scores.

## Quantitative Measures

- Prevention rate: `P = (N_blocked / N_attempted) × 100` for defined test attempts.
- Counts: unauthorized records/operations/connections; events logged; exposed services; excessive privileges removed.
- Detection coverage and false-positive observations (where measurable).
- CVSS v4.0 Base (and Threat/Environmental/Supplemental only if justified and documented).

## Finding Report Template

| Field | Content |
|---|---|
| Finding ID | e.g., DB-01 |
| Vulnerability / Weakness | Name and CWE |
| ATT&CK / CAPEC | Only where behavior matches |
| Affected component | Endpoint, role, config, or network path |
| Root cause | Technical cause |
| Evidence | Test case, logs, screenshots/captures |
| Impact | Observed confidentiality/integrity/availability |
| CVSS v4.0 | Score + full vector + justification |
| Remediation | Specific control |
| Retest | Pass/Fail with evidence |

## Quality Rules

- Same test cases, accounts, data, and initial conditions for comparisons.
- Snapshots before experiments; restore restrictive network policy after exposure tests.
- Never claim overall system security from lab measurements; report observed outcomes.
- Record exact versions and configuration for reproducibility.

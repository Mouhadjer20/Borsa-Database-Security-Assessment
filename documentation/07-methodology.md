# 07 — Research Methodology & Evaluation Framework

## 1. Experimental Methodology
This project applies a rigorous scientific comparative methodology:
For each research scenario:
1. **Hypothesis Formulation:** Define what unauthorized capability is expected.
2. **Baseline Measurement (Variant A — Vulnerable):** Execute authorized attack vector; record observations, returned data, and logs.
3. **Defense Application (Variant B / C — Remediation):** Apply defensive controls (parameterization, least privilege, RLS, network isolation).
4. **Remediation Verification:** Repeat the exact same test vector against the remediated target.
5. **Comparative Analysis:** Quantify improvement, remaining attack surface, and performance implications.

---

## 2. Threat & Vulnerability Classification Matrix

| Scenario | Weakness (CWE) | Attack Pattern (CAPEC) | MITRE ATT&CK Technique | Primary Defense |
|---|---|---|---|---|
| 1. SQL Injection | CWE-89 (Improper Neutralization) | CAPEC-66 (SQL Injection) | T1190 (Exploit Public-Facing App) | Parameterized Queries / Prepared Statements |
| 2. Excessive Privileges | CWE-250 (Execution with Unnecessary Privileges) | CAPEC-122 (Privilege Abuse) | T1078 (Valid Accounts) | Least Privilege Database Roles (GRANT/REVOKE) |
| 3. Broken Authorization | CWE-284 (Improper Access Control / BOLA) | CAPEC-1 (Accessing / Intercepting User Data) | T1530 (Data from Cloud / Local Storage Object) | Server-side Ownership Checks & PostgreSQL RLS |
| 4. Network Exposure | CWE-668 (Exposure of Resource to Wrong Sphere) | CAPEC-310 (Scanning for Vulnerable Ports) | T1046 (Network Service Discovery) | Subnet Segmentation & Host Firewalls |

---

## 3. CVSS 4.0 Scoring Approach
Assessments use the Common Vulnerability Scoring System (CVSS 4.0) to calculate realistic severity metrics:
- **Base Metrics:** Attack Vector (AV), Attack Complexity (AC), Attack Requirements (AT), Privileges Required (PR), User Interaction (UI).
- **Impact Metrics:** Confidentiality (VC/SC), Integrity (VI/SI), Availability (VA/SA).

Every score in the research report is explicitly calculated and justified based on observed laboratory data.


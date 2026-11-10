# 09 — Security Results & Comparative Analysis

## 1. Experiment Results Log

| Run ID | Scenario | Variant | Target / Payload | Result / Status | Evidence File |
|---|---|---|---|---|---|
| EXP-001 | 1. SQLi | A (Vulnerable) | `' OR '1'='1` | Demonstrated: 5 records disclosed | `evidence/logs/sqli_varA.log` |
| EXP-002 | 1. SQLi | B (Secure) | `' OR '1'='1` | Prevented: 0 records disclosed | `evidence/logs/sqli_varB.log` |
| EXP-003 | 2. Privileges | A (Overprivileged) | `SELECT rolname FROM pg_roles` | Demonstrated: System roles read | `evidence/logs/priv_varA.log` |
| EXP-004 | 2. Privileges | B (Least Privilege) | `SELECT rolname FROM pg_roles` | Prevented: Permission denied | `evidence/logs/priv_varB.log` |
| EXP-005 | 3. BOLA | A (No Check) | `account_id=2, cust_id=1` | Demonstrated: Cross-account leaked | `evidence/logs/bola_varA.log` |
| EXP-006 | 3. BOLA | B (App Check) | `account_id=2, cust_id=1` | Prevented: Filtered by app WHERE | `evidence/logs/bola_varB.log` |
| EXP-007 | 3. BOLA | C (DB RLS) | `account_id=2, cust_id=1` | Prevented: Filtered by PostgreSQL RLS | `evidence/logs/bola_varC.log` |
| EXP-008 | 4. Net Exposure | A (Segmented) | Port 5432 from VM1 | Prevented: Connection timed out | `evidence/logs/nmap_varA.log` |
| EXP-009 | 4. Net Exposure | B (Exposed) | Port 5432 from VM1 | Demonstrated: Port open & accepting | `evidence/logs/nmap_varB.log` |

---

## 2. Quantitative Comparative Evaluation

### Attack Success Rate Comparison
```
Scenario 1 (SQLi):         Variant A: 100% exploit  |  Variant B: 0% exploit
Scenario 2 (Privileges):   Variant A: 100% breach   |  Variant B: 0% breach
Scenario 3 (BOLA):         Variant A: 100% leak     |  Variant B: 0% leak  |  Variant C: 0% leak
Scenario 4 (Network):      Variant B: 100% exposed  |  Variant A: 0% exposed
```

---

## 3. Defense-in-Depth Analysis: Application Layer vs Database Layer
- **Application Controls:** Fast, easy to implement in FastAPI services, but vulnerable to developer oversight.
- **Database Controls (RLS / Role Privileges):** Provide centralized, engine-level policy enforcement that protects data even if an application SQLi or logic bug occurs.
- **Network Controls:** Ensure direct attack surfaces remain completely unreachable from unauthorized zones.


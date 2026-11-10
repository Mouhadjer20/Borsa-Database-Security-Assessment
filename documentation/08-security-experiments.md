# 08 — Security Experiments & Research Scenarios

## Scenario 1: SQL Injection (SQLi) — CWE-89

### 1. Research Objective
Determine whether dynamic SQL query formatting enables an adversary to alter backend query structure to bypass authentication or extract arbitrary customer records.

### 2. Execution Procedure
From VM 1 (Kali):
```bash
# Test Variant A (Vulnerable Concatenation)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/sqli \
  -H "Content-Type: application/json" \
  -d '{"variant": "A", "payload": "'\'' OR '\''1'\''='\''1"}'

# Test Variant B (Secure Parameterized Bind)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/sqli \
  -H "Content-Type: application/json" \
  -d '{"variant": "B", "payload": "'\'' OR '\''1'\''='\''1"}'
```

### 3. Observed Outcome
- **Variant A:** Returns multiple user records; authentication logic negated.
- **Variant B:** Returns 0 rows; payload treated as literal username.

---

## Scenario 2: Excessive Database Privileges — CWE-250

### 1. Research Objective
Demonstrate the blast radius when an application connects to PostgreSQL using an overprivileged identity versus least-privilege roles.

### 2. Execution Procedure
```bash
# Test Variant A (Overprivileged Role: app_vulnerable)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/privileges \
  -H "Content-Type: application/json" \
  -d '{"variant": "A", "payload": "SELECT rolname FROM pg_roles LIMIT 5"}'

# Test Variant B (Least Privilege Role: app_readonly)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/privileges \
  -H "Content-Type: application/json" \
  -d '{"variant": "B", "payload": "SELECT rolname FROM pg_roles LIMIT 5"}'
```

### 3. Observed Outcome
- **Variant A:** Successfully extracts database roles and system catalog information.
- **Variant B:** PostgreSQL rejects execution with `permission denied for table pg_roles`.

---

## Scenario 3: Broken Object-Level Authorization (BOLA) — CWE-284

### 1. Research Objective
Evaluate whether Customer A can view Customer B's financial balances when manipulating account IDs, comparing application-level checks and PostgreSQL Row-Level Security.

### 2. Execution Procedure
```bash
# Variant A (Missing Check - IDOR)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/bola \
  -H "Content-Type: application/json" \
  -d '{"variant": "A", "parameters": {"target_account_id": 2, "authenticated_customer_id": 1}}'

# Variant B (Application Layer Check)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/bola \
  -H "Content-Type: application/json" \
  -d '{"variant": "B", "parameters": {"target_account_id": 2, "authenticated_customer_id": 1}}'

# Variant C (PostgreSQL Row-Level Security)
curl -X POST http://192.168.100.20:8000/api/lab/experiments/bola \
  -H "Content-Type: application/json" \
  -d '{"variant": "C", "parameters": {"target_account_id": 2, "authenticated_customer_id": 1}}'
```

### 3. Observed Outcome
- **Variant A:** Unauthorized account balance disclosed.
- **Variant B:** Application returns 0 rows (ownership check enforced in query).
- **Variant C:** PostgreSQL storage engine filters rows via RLS policy.

---

## Scenario 4: Database Network Exposure — CWE-668

### 1. Research Objective
Assess the exposure risk of the PostgreSQL service when exposed directly to the audit network vs restricted strictly to the dual-homed application server.

### 2. Execution Procedure from Kali (VM 1)
```bash
# Port scan against Database Server IP
nmap -sS -p 5432 192.168.200.30

# Direct psql connection attempt from Kali
psql -h 192.168.200.30 -U app_readonly -d borsa
```

### 3. Observed Outcome
- **Secured Configuration:** Packets dropped / filtered by network routing and firewall rules.
- **Exposed Configuration:** Port 5432 open; direct database brute-force or exploitation enabled.

---

## Vulnerability Chaining
Investigate compound attack paths:
1. SQL injection allows query manipulation.
2. Excessive database privileges allow writing into arbitrary tables or reading catalog secrets.
3. Network exposure enables direct exploitation bypassing application auditing.
*Remediation at any single layer breaks the chain, illustrating defense-in-depth.*


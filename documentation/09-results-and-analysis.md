# 09 — Security Results & Comparative Analysis

## 1. Experiment Results Log (CTF Assessment)

| Run ID | Scenario (CWE) | Target Endpoint | Payload / Technique | Observed Result | Risk Level |
|---|---|---|---|---|---|
| EXP-001 | 1. SQLi (CWE-89) | `GET /api/auth/search?q=` | `' OR '1'='1` | **Vulnerable:** All user records extracted; authentication boundaries bypassed | Critical |
| EXP-002 | 1. SQLi (CWE-89) | `GET /api/auth/search?q=` | `' UNION SELECT username, password_hash, role FROM app_users --` | **Vulnerable:** Exfiltrates bcrypt password hashes from `app_users` table | Critical |
| EXP-003 | 2. Excessive Privileges (CWE-250) | `GET /api/transactions/export` | Normal query with `limit=1` | **Vulnerable:** Leaks database username (`app_writer`), server PID, and full PostgreSQL version | Medium |
| EXP-004 | 2. Excessive Privileges (CWE-250) | `GET /api/auth/search?q=` + privilege query | Query `information_schema.role_table_grants` via SQLi | **Vulnerable:** Exposes entire database permissions matrix to authenticated users | High |
| EXP-005 | 3. BOLA / IDOR (CWE-284) | `GET /api/accounts/lookup/{id}` | Access account `3` while logged in as `alice` (owner of `1`, `2`) | **Vulnerable:** Returns Customer B's account balance and details without ownership check | High |
| EXP-006 | 3. BOLA / IDOR (CWE-284) | `GET /api/accounts/{id}` | Access account `3` while logged in as `alice` | **Protected:** Returns `403 Forbidden` — application-layer ownership check enforced | Informational |
| EXP-007 | 4. SSRF / Exposure (CWE-668) | `GET /api/diagnostics/db-ping?host=&port=` | `host=192.168.56.2&port=5432` | **Vulnerable:** TCP connection state disclosed; bypasses perimeter firewall to probe internal DB | High |
| EXP-008 | 4. SSRF / Exposure (CWE-668) | `GET /api/diagnostics/db-ping?host=&port=` | `host=127.0.0.1&port=8000` | **Vulnerable:** Internal port scan discovers internal Uvicorn service | Medium |

---

## 2. Comparative Evaluation: Vulnerable CTF Endpoints vs Enforced Counterparts

| Dimension | Vulnerable Implementation | Hardened / Enforced Counterpart | Impact of Fix |
|---|---|---|---|
| **SQLi (`/api/auth/search`)** | String interpolation: `f"SELECT ... WHERE username LIKE '%{q}%'"` | Parameterized query: `select(AppUser).where(AppUser.username.ilike(bindparam('q')))` | Eliminates query injection; 100% exploit prevention |
| **BOLA (`/api/accounts/lookup`)** | Unfiltered lookup: `SELECT ... WHERE account_id = :id` | Ownership check: `WHERE account_id = :id AND customer_id = :current_user_id` | Blocks unauthorized cross-account visibility |
| **Excessive Privileges (`/api/transactions/export`)** | Returns `session_metadata` with DB user and engine version | Strip metadata; connect as `app_readonly` with restricted catalog access | Prevents reconnaissance; limits blast radius |
| **Network SSRF (`/api/diagnostics/db-ping`)** | Arbitrary host & port input accepted from user | Restrict to allowlisted `settings.db_host` and `settings.db_port` only | Prevents internal network enumeration and pivoting |

---

## 3. Defense-in-Depth Analysis

- **Application Layer:** Input validation, strict parameter binding, and customer ownership checks (`customer_id == current_user.customer_id`) provide the first line of defense.
- **Database Layer (Least Privilege & RLS):** The application should connect as `app_readonly` for read operations and `app_writer` strictly for mutations. Sensitive tables (`security_audit`, `access_policies`) should only be accessible to dedicated audit roles.
- **Network Layer (Firewall Segmentation):** VM2's PostgreSQL port `5432` is restricted via UFW to accept connections exclusively from VM1's IP (`192.168.56.3`). Even if an external adversary accesses the network, the database cannot be reached directly without pivoting through the application server.

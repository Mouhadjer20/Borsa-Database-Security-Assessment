# 06 — Database Design (Draft)

## Conceptual Model

| Table | Key fields (conceptual) | Purpose |
|---|---|---|
| `customers` | `customer_id`, `full_name`, `email`, `status` | Synthetic customer identity |
| `bank_accounts` | `account_id`, `customer_id`, `account_type`, `balance`, `currency`, `status` | Account ownership and balances |
| `transactions` | `transaction_id`, `source_account`, `destination_account`, `amount`, `timestamp`, `status` | Synthetic transaction history |
| `employees` | `employee_id`, `name`, `department`, `status` | Internal staff records |
| `app_users` | `user_id`, `username`, `password_hash`, `role` | Application authentication identities |
| `security_audit` | `event_id`, `actor`, `action`, `resource`, `timestamp` | Application/security event records |
| `access_policies` | `policy_id`, `role`, `resource`, `permission` | Conceptual authorization mapping (refine in implementation) |

Relationships (to finalize before SQL): customers → bank_accounts; bank_accounts ↔ transactions; app_users/roles → authorization decisions; audit references actors/resources.

## Identity Separation

Application users (`app_users`) are **not** PostgreSQL roles. PostgreSQL roles control database privileges; application logic controls user authentication and may establish trusted session context (documented carefully if RLS uses session settings).

## PostgreSQL Roles (planned)

| Role | Purpose |
|---|---|
| `db_owner` | Controlled object ownership/administration |
| `app_readonly` | Read-only application operations |
| `app_writer` | Limited application write operations |
| `app_vulnerable` | Deliberately overprivileged experimental identity (not superuser/admin) |
| `auditor` | Authorized security inspection |
| `migration_role` | Controlled schema migrations |

Runtime application must not connect as superuser.

## Synthetic Data & Canaries

- Customers A/B/C own accounts A/B/C; Employee D and Administrator E have defined permissions.
- Include distinctive canary records (unique customer/account/transaction markers) unused by normal workflows to make unauthorized access unambiguous.

## Authorization Comparison (extension)

| Variant | Mechanism | Notes |
|---|---|---|
| B | Server-side application ownership checks | Enforced in FastAPI/service layer |
| C | PostgreSQL RLS | DB-enforced row access; requires correct role/session identity |

RLS is evaluated only when session identity is correctly established and cannot be manipulated by untrusted input.

## SQL/PostgreSQL Notes

- Use standard SQL where practical; document PostgreSQL-specific features (RLS, roles, config, extensions).
- Prefer parameterized queries/prepared statements; never construct SQL from untrusted input in secured variant.
- Record exact schema, grants, policies, and seed version for reproducibility.

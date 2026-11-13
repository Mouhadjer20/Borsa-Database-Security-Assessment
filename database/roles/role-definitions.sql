-- =============================================================================
-- BORSA DATABASE ROLES & PRIVILEGE DEFINITIONS
-- =============================================================================
-- ⚠️ REFERENCE ONLY — Provisioned by DBA on PostgreSQL 18.x Server
-- =============================================================================

-- 1. db_owner: Owns database objects, performs administrative maintenance
-- (Never used for normal runtime application traffic)
CREATE ROLE db_owner WITH LOGIN PASSWORD 'change_in_production_db_owner';

-- 2. app_readonly: Least-privileged role for read operations in Secure Mode
CREATE ROLE app_readonly WITH LOGIN PASSWORD 'change_in_production_readonly';
GRANT CONNECT ON DATABASE borsa TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON customers, bank_accounts, transactions, employees, app_users TO app_readonly;
GRANT INSERT ON security_audit TO app_readonly;
GRANT USAGE, SELECT ON SEQUENCE security_audit_event_id_seq TO app_readonly;

-- 3. app_writer: Least-privileged role for write/update operations in Secure Mode
CREATE ROLE app_writer WITH LOGIN PASSWORD 'change_in_production_writer';
GRANT CONNECT ON DATABASE borsa TO app_writer;
GRANT USAGE ON SCHEMA public TO app_writer;
GRANT SELECT, INSERT, UPDATE ON bank_accounts, transactions TO app_writer;
GRANT SELECT ON customers, app_users TO app_writer;
GRANT SELECT, INSERT ON security_audit TO app_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_writer;

-- 4. app_vulnerable: Deliberately overprivileged identity for isolated Security Lab tests
-- Intentionally granted excessive privileges (SELECT on all tables, system catalogs, DDL permissions)
-- MUST ONLY BE BOUND TO ISOLATED LABORATORY NETWORK & SYNTHETIC DATABASE
CREATE ROLE app_vulnerable WITH LOGIN PASSWORD 'change_in_production_vulnerable';
GRANT CONNECT ON DATABASE borsa TO app_vulnerable;
GRANT USAGE ON SCHEMA public TO app_vulnerable;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_vulnerable;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_vulnerable;

-- 5. auditor: Read-only inspection role for security reviewers
CREATE ROLE auditor WITH LOGIN PASSWORD 'change_in_production_auditor';
GRANT CONNECT ON DATABASE borsa TO auditor;
GRANT USAGE ON SCHEMA public TO auditor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO auditor;

-- 6. migration_role: Dedicated DDL maintenance role outside runtime execution
CREATE ROLE migration_role WITH LOGIN PASSWORD 'change_in_production_migration';
GRANT ALL ON SCHEMA public TO migration_role;


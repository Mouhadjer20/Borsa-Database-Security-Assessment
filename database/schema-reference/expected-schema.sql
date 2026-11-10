-- =============================================================================
-- BORSA FINANCIAL DATABASE SCHEMA REFERENCE
-- =============================================================================
-- ⚠️ REFERENCE ONLY — DO NOT EXECUTE AGAINST LIVE APPLICATION DATABASE.
--
-- In accordance with project rules, the application does not execute DDL
-- statements or automatic migrations. The existing PostgreSQL 18.x database
-- is provisioned separately by the database administrator.
--
-- This file documents the expected logical and physical relational structure.
-- =============================================================================

-- 1. customers: Profile data for financial clients
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    full_name   VARCHAR(255) NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    status      VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. bank_accounts: Deposit, savings, and investment accounts
CREATE TABLE IF NOT EXISTS bank_accounts (
    account_id    SERIAL PRIMARY KEY,
    customer_id   INTEGER NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    account_type  VARCHAR(50) NOT NULL DEFAULT 'checking',
    balance       NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    currency      VARCHAR(3) NOT NULL DEFAULT 'USD',
    status        VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. transactions: Ledger entries for money movements
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id      SERIAL PRIMARY KEY,
    source_account      INTEGER REFERENCES bank_accounts(account_id),
    destination_account INTEGER REFERENCES bank_accounts(account_id),
    amount              NUMERIC(15, 2) NOT NULL,
    status              VARCHAR(50) NOT NULL DEFAULT 'completed',
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. employees: Bank personnel directory
CREATE TABLE IF NOT EXISTS employees (
    employee_id SERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    department  VARCHAR(100) NOT NULL,
    status      VARCHAR(50) NOT NULL DEFAULT 'active'
);

-- 5. app_users: Application authentication records
CREATE TABLE IF NOT EXISTS app_users (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role          VARCHAR(50) NOT NULL DEFAULT 'customer',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. security_audit: Application and security event audit trail
CREATE TABLE IF NOT EXISTS security_audit (
    event_id  BIGSERIAL PRIMARY KEY,
    actor     VARCHAR(150) NOT NULL,
    action    VARCHAR(100) NOT NULL,
    resource  VARCHAR(255) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 7. access_policies: Role-based access control policies
CREATE TABLE IF NOT EXISTS access_policies (
    policy_id  SERIAL PRIMARY KEY,
    role       VARCHAR(50) NOT NULL,
    resource   VARCHAR(100) NOT NULL,
    permission VARCHAR(50) NOT NULL
);

-- Indexes for performance and query isolation
CREATE INDEX IF NOT EXISTS idx_bank_accounts_customer ON bank_accounts(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source_account);
CREATE INDEX IF NOT EXISTS idx_transactions_dest ON transactions(destination_account);
CREATE INDEX IF NOT EXISTS idx_security_audit_timestamp ON security_audit(timestamp DESC);


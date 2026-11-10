-- =============================================================================
-- BORSA POSTGRESQL ROW-LEVEL SECURITY (RLS) POLICIES
-- =============================================================================
-- ⚠️ REFERENCE ONLY — Demonstrates database-enforced multi-tenant isolation
-- =============================================================================

-- Enable Row-Level Security on bank_accounts
ALTER TABLE bank_accounts ENABLE ROW LEVEL SECURITY;

-- Force RLS even for table owners (optional strict mode)
-- ALTER TABLE bank_accounts FORCE ROW LEVEL SECURITY;

-- Policy: Customers can only select accounts where customer_id matches session context
CREATE POLICY account_customer_isolation_policy ON bank_accounts
    FOR ALL
    TO app_readonly, app_writer
    USING (
        customer_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
    )
    WITH CHECK (
        customer_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
    );

-- Enable Row-Level Security on transactions
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- Policy: Customers can only view transactions where their account is source or destination
CREATE POLICY transaction_customer_isolation_policy ON transactions
    FOR SELECT
    TO app_readonly, app_writer
    USING (
        source_account IN (
            SELECT account_id FROM bank_accounts
            WHERE customer_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
        )
        OR
        destination_account IN (
            SELECT account_id FROM bank_accounts
            WHERE customer_id = NULLIF(current_setting('app.current_user_id', true), '')::integer
        )
    );


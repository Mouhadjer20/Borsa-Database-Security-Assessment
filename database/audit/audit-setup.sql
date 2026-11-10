-- =============================================================================
-- BORSA DATABASE AUDITING SETUP
-- =============================================================================
-- ⚠️ REFERENCE ONLY — Configured by DBA for security event logging
-- =============================================================================

-- 1. Enable pgaudit extension (if available in PostgreSQL 18.x installation)
-- CREATE EXTENSION IF NOT EXISTS pgaudit;
-- ALTER SYSTEM SET pgaudit.log = 'write, ddl, role';
-- SELECT pg_reload_conf();

-- 2. Audit trigger function for sensitive financial modifications
CREATE OR REPLACE FUNCTION audit_financial_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO security_audit (actor, action, resource, timestamp)
    VALUES (
        COALESCE(current_setting('app.current_user_id', true), session_user),
        TG_OP,
        TG_TABLE_NAME || ' ID: ' || COALESCE(NEW.account_id::text, OLD.account_id::text, 'unknown'),
        CURRENT_TIMESTAMP
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Attach trigger to bank_accounts for INSERT / UPDATE / DELETE
DROP TRIGGER IF EXISTS trg_audit_bank_accounts ON bank_accounts;
CREATE TRIGGER trg_audit_bank_accounts
    AFTER INSERT OR UPDATE OR DELETE ON bank_accounts
    FOR EACH ROW EXECUTE FUNCTION audit_financial_changes();


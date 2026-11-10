-- =============================================================================
-- BORSA — Development Seed Data
-- =============================================================================
-- Run this ONCE against a freshly created database (after expected-schema.sql).
-- WARNING: These are INTENTIONALLY WEAK demo credentials for local dev only.
-- Never use in production.
-- =============================================================================

-- Customers
INSERT INTO customers (full_name, email, status) VALUES
  ('Alice Nguyen',   'alice@borsa.local',   'active'),
  ('Bob Markov',     'bob@borsa.local',     'active'),
  ('Charlie Durand', 'charlie@borsa.local', 'active'),
  ('Diana Prince',   'diana@borsa.local',   'active'),
  ('Admin User',     'admin@borsa.local',   'active')
ON CONFLICT (email) DO NOTHING;

-- Bank accounts
INSERT INTO bank_accounts (customer_id, account_type, balance, currency, status) VALUES
  (1, 'checking', 12450.00, 'USD', 'active'),
  (1, 'savings',  38200.00, 'USD', 'active'),
  (2, 'checking',  5700.00, 'USD', 'active'),
  (3, 'savings',  22100.00, 'USD', 'active'),
  (4, 'checking',  3300.00, 'USD', 'active')
ON CONFLICT DO NOTHING;

-- Transactions
INSERT INTO transactions (source_account, destination_account, amount, status) VALUES
  (1, 3, 500.00,  'completed'),
  (3, 2, 1200.00, 'completed'),
  (2, 4, 300.00,  'completed'),
  (4, 1, 750.00,  'completed'),
  (1, 5, 100.00,  'completed')
ON CONFLICT DO NOTHING;

-- App users
-- Passwords are bcrypt-hashed (rounds=12). Plaintext values:
--   alice   → password: alice1234
--   bob     → password: bob1234
--   charlie → password: charlie1234
--   diana   → password: diana1234
--   admin   → password: adminpass1
INSERT INTO app_users (username, password_hash, role) VALUES
  ('alice',   '$2b$12$wQHE/2N6Rwqo4nzWeUXttO86KKzHJOG48zy71lByqpKzYk.MA5mNS', 'customer'),
  ('bob',     '$2b$12$c/Idt5HczDuPrRNMVlgbtOZmc5oga2dAjgaInVa6Q/P23Pdl3POtS', 'customer'),
  ('charlie', '$2b$12$UF7ad6VmW0pxNucLRL6dvOtgrv7K0JQ3HYUYPX6ATB.xBXs/MnKHG', 'customer'),
  ('diana',   '$2b$12$Xk3XC0ZNaI0vMZpWdH/VBOzFlZ0rt9LT4xjoUc09FC22DenKgJBmS', 'customer'),
  ('admin',   '$2b$12$YBrVD1usRat3xl0fUOzajOnSCZTXdxo.vPXplly5CcoQsKWohmLCe', 'admin')
ON CONFLICT (username) DO NOTHING;


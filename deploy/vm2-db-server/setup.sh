#!/usr/bin/env bash
# =============================================================================
# VM2 — Database Server Setup
# =============================================================================
# Installs PostgreSQL, creates the borsa database, roles, schema, and seed data.
#
# Target OS : Ubuntu 22.04 / 24.04 LTS (Debian-based)
# Run as    : sudo bash setup.sh
# Usage     : sudo bash setup.sh [--app-ip <VM1_IP>] [--db-password <PASS>]
#
# Example   : sudo bash setup.sh --app-ip 192.168.1.5 --db-password Secret42!
# =============================================================================
set -euo pipefail

# --------------------------------------------------------------------------- #
# Helper: first non-loopback IPv4 address (portable: Linux & macOS/BSD)
# --------------------------------------------------------------------------- #
get_first_ip() {
  if command -v ip >/dev/null 2>&1; then
    # Linux (iproute2)
    ip -o -f inet addr show 2>/dev/null | awk '/scope global/ {print $4; exit}' | cut -d/ -f1
  elif command -v ifconfig >/dev/null 2>&1; then
    # macOS / BSD
    ifconfig 2>/dev/null | awk '/inet / && $2 !~ /^127\./ {gsub(/addr:/,"",$2); print $2; exit}'
  else
    python3 -c "import socket; print(socket.gethostbyname(socket.gethostname()))" 2>/dev/null || true
  fi
}

# --------------------------------------------------------------------------- #
# Configurable defaults (override via CLI flags)
# --------------------------------------------------------------------------- #
APP_IP="192.168.1.5"       # IP of VM1 (App Server) — allow pg connections
DB_NAME="borsa_db"
DB_OWNER_PASS="BorsaOwner$(openssl rand -hex 6)"
DB_WRITER_PASS="BorsaWriter$(openssl rand -hex 6)"
DB_READONLY_PASS="BorsaRead$(openssl rand -hex 6)"
SEED_DATA="YES"               # Set to NO to skip seeding

# --------------------------------------------------------------------------- #
# Parse flags
# --------------------------------------------------------------------------- #
while [[ $# -gt 0 ]]; do
  case "$1" in
    --app-ip)      APP_IP="$2";       shift 2 ;;
    --db-password) DB_WRITER_PASS="$2"; DB_READONLY_PASS="$2"; shift 2 ;;
    --no-seed)     SEED_DATA="NO";    shift ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# --------------------------------------------------------------------------- #
# Colours
# --------------------------------------------------------------------------- #
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
die()     { echo -e "${RED}[FAIL]${NC} $*" >&2; exit 1; }

# --------------------------------------------------------------------------- #
# 0. Must run as root
# --------------------------------------------------------------------------- #
[[ $EUID -eq 0 ]] || die "Run with: sudo bash $0"

info "=== BorsaTrust — VM2 Database Server Setup ==="
info "App Server IP : $APP_IP"
info "Database name : $DB_NAME"
echo

# --------------------------------------------------------------------------- #
# 1. System packages
# --------------------------------------------------------------------------- #
info "Updating package lists…"
apt-get update -qq

info "Installing PostgreSQL 16…"
apt-get install -y -qq postgresql postgresql-contrib curl ca-certificates ufw

PG_VERSION=$(pg_lsclusters | awk 'NR==2{print $1}')
PG_CONF_DIR="/etc/postgresql/${PG_VERSION}/main"
info "Detected PostgreSQL version: $PG_VERSION"

# --------------------------------------------------------------------------- #
# 2. Configure PostgreSQL to listen on all interfaces
# --------------------------------------------------------------------------- #
info "Configuring postgresql.conf (listen_addresses)…"
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF_DIR/postgresql.conf"

# --------------------------------------------------------------------------- #
# 3. Configure pg_hba.conf — allow app server connections
# --------------------------------------------------------------------------- #
info "Configuring pg_hba.conf for VM1 ($APP_IP)…"
PG_HBA="$PG_CONF_DIR/pg_hba.conf"

# Remove any existing borsa entries to avoid duplicates
grep -v "# borsa-ctf" "$PG_HBA" > /tmp/pg_hba_clean.conf || true
cp /tmp/pg_hba_clean.conf "$PG_HBA"

cat >> "$PG_HBA" <<EOF

# borsa-ctf — allow app server roles to connect
host    $DB_NAME    app_writer    $APP_IP/32    scram-sha-256
host    $DB_NAME    app_readonly  $APP_IP/32    scram-sha-256
# borsa-ctf — allow local superuser (for DBA tasks)
local   all         postgres                    peer
EOF

success "pg_hba.conf updated"

# --------------------------------------------------------------------------- #
# 4. Start / restart PostgreSQL
# --------------------------------------------------------------------------- #
info "Restarting PostgreSQL service…"
systemctl enable postgresql
systemctl restart postgresql
sleep 2
success "PostgreSQL running"

# --------------------------------------------------------------------------- #
# 5. Create database and roles
# --------------------------------------------------------------------------- #
info "Creating database '$DB_NAME' and roles…"

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL

-- Create database
SELECT 'CREATE DATABASE $DB_NAME' WHERE NOT EXISTS (
  SELECT FROM pg_database WHERE datname = '$DB_NAME'
) \gexec

\connect $DB_NAME

-- app_writer role
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_writer') THEN
    CREATE ROLE app_writer WITH LOGIN PASSWORD '$DB_WRITER_PASS';
  ELSE
    ALTER ROLE app_writer WITH PASSWORD '$DB_WRITER_PASS';
  END IF;
END\$\$;

GRANT CONNECT ON DATABASE $DB_NAME TO app_writer;
GRANT USAGE ON SCHEMA public TO app_writer;

-- app_readonly role
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'app_readonly') THEN
    CREATE ROLE app_readonly WITH LOGIN PASSWORD '$DB_READONLY_PASS';
  ELSE
    ALTER ROLE app_readonly WITH PASSWORD '$DB_READONLY_PASS';
  END IF;
END\$\$;

GRANT CONNECT ON DATABASE $DB_NAME TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;

SQL

success "Database and roles created"

# --------------------------------------------------------------------------- #
# 6. Run schema SQL
# --------------------------------------------------------------------------- #
info "Applying schema…"
sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1 \
  -f "$PROJECT_ROOT/database/schema-reference/expected-schema.sql"
success "Schema applied"

# --------------------------------------------------------------------------- #
# 7. Grant privileges to roles (post-schema, so tables exist)
# --------------------------------------------------------------------------- #
info "Granting table privileges…"
sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1 <<SQL

-- app_writer: read + write on operational tables
GRANT SELECT, INSERT, UPDATE ON bank_accounts, transactions TO app_writer;
GRANT SELECT ON customers, app_users, employees, access_policies TO app_writer;
GRANT INSERT ON security_audit TO app_writer;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_writer;

-- app_readonly: SELECT only
GRANT SELECT ON customers, bank_accounts, transactions, employees,
               app_users, security_audit, access_policies TO app_readonly;
GRANT INSERT ON security_audit TO app_readonly;
GRANT USAGE, SELECT ON SEQUENCE security_audit_event_id_seq TO app_readonly;

SQL

success "Privileges granted"

# --------------------------------------------------------------------------- #
# 8. Seed data
# --------------------------------------------------------------------------- #
if [[ "$SEED_DATA" == "YES" ]]; then
  info "Seeding development data…"
  sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1 \
    -f "$PROJECT_ROOT/database/seed-data.sql"
  success "Seed data inserted"
else
  warn "Skipping seed data (--no-seed)"
fi

# --------------------------------------------------------------------------- #
# 9. UFW firewall — open PostgreSQL port only to App Server
# --------------------------------------------------------------------------- #
info "Configuring firewall (UFW)…"
ufw --force enable
ufw allow ssh
ufw allow from "$APP_IP" to any port 5432 proto tcp
ufw reload
success "Firewall configured — PostgreSQL open only to $APP_IP"

# --------------------------------------------------------------------------- #
# 10. Write credentials file for VM1 handoff
# --------------------------------------------------------------------------- #
CREDS_FILE="$SCRIPT_DIR/db-credentials.txt"
cat > "$CREDS_FILE" <<EOF
# ======================================================
# BorsaTrust — DB Credentials (copy to VM1 .env)
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# ======================================================
DB_HOST=<VM2_IP>          # Replace with this VM's IP
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=app_writer
DB_PASSWORD=$DB_WRITER_PASS
DB_SSLMODE=prefer

# Read-only role (optional, for future read-replica use):
# DB_USER=app_readonly
# DB_PASSWORD=$DB_READONLY_PASS
EOF
chmod 600 "$CREDS_FILE"

# --------------------------------------------------------------------------- #
# Done
# --------------------------------------------------------------------------- #
echo
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  VM2 Database Server setup complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo
echo "  Database : $DB_NAME"
echo "  Port     : 5432"
echo "  Roles    : app_writer / app_readonly"
echo
echo -e "${YELLOW}  Next steps:${NC}"
echo "  1. Note this VM's IP: $(get_first_ip)"
echo "  2. Credentials saved to: $CREDS_FILE"
echo "  3. Copy DB_HOST, DB_PASSWORD to VM1's .env"
echo "  4. Run vm1-app-server/setup.sh on VM1"
echo


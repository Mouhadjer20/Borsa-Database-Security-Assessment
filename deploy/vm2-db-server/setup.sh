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
# Example   : sudo bash setup.sh --app-ip 192.168.56.101 --db-password Secret42!
# =============================================================================
set -euo pipefail

# --------------------------------------------------------------------------- #
# Helper: first non-loopback IPv4 address (portable: Linux & macOS/BSD)
# --------------------------------------------------------------------------- #
get_first_ip() {
  if command -v ip >/dev/null 2>&1; then
    ip -o -f inet addr show 2>/dev/null | awk '/scope global/ {print $4; exit}' | cut -d/ -f1
  elif command -v ifconfig >/dev/null 2>&1; then
    ifconfig 2>/dev/null | awk '/inet / && $2 !~ /^127\./ {gsub(/addr:/,"",$2); print $2; exit}'
  else
    python3 -c "import socket; print(socket.gethostbyname(socket.gethostname()))" 2>/dev/null || true
  fi
}

# --------------------------------------------------------------------------- #
# Configurable defaults (override via CLI flags)
# --------------------------------------------------------------------------- #
APP_IP="192.168.56.101"       # IP of VM1 (App Server) — allow pg connections
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

# Network sanity warning for VirtualBox default NAT
if [[ "$APP_IP" == "10.0.2.15" ]]; then
  echo
  warn "------------------------------------------------------------------------"
  warn "WARNING: 10.0.2.15 is VirtualBox's default isolated NAT IP."
  warn "Under default 'NAT' adapter, VMs CANNOT reach each other on 10.0.2.15!"
  warn "For two VMs to communicate in VirtualBox, you should configure either:"
  warn "  1) 'Host-Only Adapter' (recommended, e.g. 192.168.56.x)"
  warn "  2) 'Internal Network' or 'NAT Network' (with custom IPs)"
  warn "  3) 'Bridged Adapter' (receives an IP from your home/LAN router)"
  warn "------------------------------------------------------------------------"
  echo
fi

# --------------------------------------------------------------------------- #
# 1. System packages
# --------------------------------------------------------------------------- #
info "Updating package lists…"
apt-get update -qq

info "Installing PostgreSQL…"
apt-get install -y -qq postgresql postgresql-contrib curl ca-certificates ufw

# Ensure PostgreSQL service is started
systemctl enable postgresql
systemctl start postgresql

# --------------------------------------------------------------------------- #
# 2. Locate PostgreSQL configuration files dynamically
# --------------------------------------------------------------------------- #
PG_CONF=$(sudo -u postgres psql -t -P format=unaligned -c "SHOW config_file;" 2>/dev/null || true)
PG_HBA=$(sudo -u postgres psql -t -P format=unaligned -c "SHOW hba_file;" 2>/dev/null || true)

if [[ -z "$PG_CONF" || ! -f "$PG_CONF" ]]; then
  PG_VERSION=$(pg_lsclusters -h 2>/dev/null | awk '{print $1; exit}' || echo "16")
  PG_CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"
  PG_HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"
fi

info "Config file : $PG_CONF"
info "HBA file    : $PG_HBA"

# --------------------------------------------------------------------------- #
# 3. Configure postgresql.conf (listen_addresses = '*')
# --------------------------------------------------------------------------- #
info "Configuring postgresql.conf (listen_addresses)…"
if grep -E "^[#]?[ \t]*listen_addresses" "$PG_CONF" >/dev/null 2>&1; then
  sed -i -E "s/^[#]?[ \t]*listen_addresses[ \t]*=.*/listen_addresses = '*'/" "$PG_CONF"
else
  echo "listen_addresses = '*'" >> "$PG_CONF"
fi
success "postgresql.conf configured to listen on all interfaces"

# --------------------------------------------------------------------------- #
# 4. Configure pg_hba.conf — allow app server connections
# --------------------------------------------------------------------------- #
info "Configuring pg_hba.conf for VM1 ($APP_IP)…"

# Determine CIDR (don't append /32 if user already specified a subnet)
APP_CIDR="$APP_IP"
[[ "$APP_CIDR" =~ / ]] || APP_CIDR="${APP_IP}/32"

# Remove any previously added block to make the script safely idempotent
sed -i '/### BEGIN BORSA-CTF ###/,/### END BORSA-CTF ###/d' "$PG_HBA"

cat >> "$PG_HBA" <<EOF
### BEGIN BORSA-CTF ###
# Allow Borsa application server roles from $APP_CIDR
host    $DB_NAME    app_writer    $APP_CIDR    scram-sha-256
host    $DB_NAME    app_readonly  $APP_CIDR    scram-sha-256
### END BORSA-CTF ###
EOF

success "pg_hba.conf updated cleanly"

# --------------------------------------------------------------------------- #
# 5. Restart PostgreSQL to apply network & auth changes
# --------------------------------------------------------------------------- #
info "Restarting PostgreSQL service…"
systemctl restart postgresql
sleep 2
systemctl is-active --quiet postgresql || die "PostgreSQL failed to restart — check /var/log/postgresql/"
success "PostgreSQL is running"

# --------------------------------------------------------------------------- #
# 6. Create database and roles
# --------------------------------------------------------------------------- #
info "Creating database '$DB_NAME' and roles…"

sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL

-- Create database if not exists
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
# 7. Run schema SQL (Piped via stdin to avoid permission denied on /home paths)
# --------------------------------------------------------------------------- #
SCHEMA_FILE="$PROJECT_ROOT/database/schema-reference/expected-schema.sql"
[[ -f "$SCHEMA_FILE" ]] || die "Schema file not found at: $SCHEMA_FILE"

info "Applying schema…"
cat "$SCHEMA_FILE" | sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1
success "Schema applied successfully"

# --------------------------------------------------------------------------- #
# 8. Grant privileges to roles (tables now exist)
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
# 9. Seed data (Piped via stdin to avoid permission denied on /home paths)
# --------------------------------------------------------------------------- #
if [[ "$SEED_DATA" == "YES" ]]; then
  SEED_FILE="$PROJECT_ROOT/database/seed-data.sql"
  [[ -f "$SEED_FILE" ]] || die "Seed file not found at: $SEED_FILE"

  info "Seeding development data…"
  # Reset any existing rows before seeding to avoid duplicates on re-run
  sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1 -c "
    TRUNCATE security_audit, transactions, bank_accounts, customers, app_users RESTART IDENTITY CASCADE;
  "
  cat "$SEED_FILE" | sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1
  success "Seed data inserted"
else
  warn "Skipping seed data (--no-seed)"
fi

# --------------------------------------------------------------------------- #
# 10. UFW firewall — open PostgreSQL port only to App Server
# --------------------------------------------------------------------------- #
info "Configuring firewall (UFW)…"
if command -v ufw >/dev/null 2>&1; then
  ufw --force enable || true
  ufw allow ssh || true
  ufw allow from "$APP_IP" to any port 5432 proto tcp || true
  ufw reload || true
  success "Firewall configured — PostgreSQL open only to $APP_IP"
else
  warn "UFW not found, skipping firewall configuration"
fi

# --------------------------------------------------------------------------- #
# 11. Write credentials file for VM1 handoff
# --------------------------------------------------------------------------- #
CREDS_FILE="$SCRIPT_DIR/db-credentials.txt"
MY_IP="$(get_first_ip)"
cat > "$CREDS_FILE" <<EOF
# ======================================================
# BorsaTrust — DB Credentials (copy to VM1 setup)
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# ======================================================
DB_HOST=$MY_IP
DB_PORT=5432
DB_NAME=$DB_NAME
DB_USER=app_writer
DB_PASSWORD=$DB_WRITER_PASS
DB_SSLMODE=prefer
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
echo "  User     : app_writer"
echo "  Password : $DB_WRITER_PASS"
echo "  Host IP  : $MY_IP"
echo
echo -e "${YELLOW}  Credentials saved to:${NC} $CREDS_FILE"
echo
echo -e "${YELLOW}  Next step on VM1 (App Server):${NC}"
echo "    sudo bash deploy/vm1-app-server/setup.sh \\"
echo "        --db-host $MY_IP \\"
echo "        --db-pass $DB_WRITER_PASS \\"
echo "        --frontend-origin http://<VM1_IP>"
echo

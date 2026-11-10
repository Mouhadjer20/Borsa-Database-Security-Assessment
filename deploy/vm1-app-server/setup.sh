#!/usr/bin/env bash
# =============================================================================
# VM1 — Application Server Setup
# =============================================================================
# Installs Python 3.11, Node.js 20, Nginx. Builds the React frontend,
# installs the FastAPI backend, creates a systemd service, and configures
# Nginx to serve everything on port 80.
#
# Target OS : Ubuntu 22.04 / 24.04 LTS (Debian-based)
# Run as    : sudo bash setup.sh
# Usage     : sudo bash setup.sh [--db-host <VM2_IP>] [--db-pass <PASS>]
#                                [--frontend-origin <URL>] [--app-secret <SECRET>]
#
# Example   : sudo bash setup.sh \
#               --db-host 192.168.1.5 \
#               --db-pass Secret42! \
#               --frontend-origin http://192.168.1.5
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
DB_HOST="192.168.1.5"
DB_PORT="5432"
DB_NAME="borsa_db"
DB_USER="app_writer"
DB_PASS="changeme"
DB_SSLMODE="prefer"
APP_PORT="8000"
APP_SECRET="$(openssl rand -hex 32)"
FRONTEND_ORIGIN="http://$(get_first_ip)"
DEPLOY_USER="${SUDO_USER:-borsa}"

# --------------------------------------------------------------------------- #
# Parse flags
# --------------------------------------------------------------------------- #
while [[ $# -gt 0 ]]; do
  case "$1" in
    --db-host)           DB_HOST="$2";           shift 2 ;;
    --db-port)           DB_PORT="$2";           shift 2 ;;
    --db-name)           DB_NAME="$2";           shift 2 ;;
    --db-user)           DB_USER="$2";           shift 2 ;;
    --db-pass)           DB_PASS="$2";           shift 2 ;;
    --db-sslmode)        DB_SSLMODE="$2";        shift 2 ;;
    --app-secret)        APP_SECRET="$2";        shift 2 ;;
    --frontend-origin)   FRONTEND_ORIGIN="$2";   shift 2 ;;
    --deploy-user)       DEPLOY_USER="$2";       shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
APP_DIR="/opt/borsa"

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

info "=== BorsaTrust — VM1 Application Server Setup ==="
info "Database host   : $DB_HOST:$DB_PORT"
info "Frontend origin : $FRONTEND_ORIGIN"
info "App directory   : $APP_DIR"
echo

# --------------------------------------------------------------------------- #
# 1. System packages
# --------------------------------------------------------------------------- #
info "Updating package lists…"
apt-get update -qq

info "Installing system dependencies…"
apt-get install -y -qq \
  python3.11 python3.11-venv python3.11-dev python3-pip \
  build-essential libpq-dev \
  nginx curl ca-certificates ufw git

# --------------------------------------------------------------------------- #
# 2. Node.js 20 (via NodeSource)
# --------------------------------------------------------------------------- #
if ! command -v node &>/dev/null || [[ "$(node --version | cut -d. -f1 | tr -d 'v')" -lt 20 ]]; then
  info "Installing Node.js 20…"
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y -qq nodejs
fi
success "Node.js $(node --version) ready"

# --------------------------------------------------------------------------- #
# 3. Create app user and directory
# --------------------------------------------------------------------------- #
if ! id borsa &>/dev/null; then
  info "Creating system user 'borsa'…"
  useradd --system --no-create-home --shell /usr/sbin/nologin borsa
fi

info "Copying project to $APP_DIR…"
mkdir -p "$APP_DIR"
rsync -a --delete \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude 'dist' \
  --exclude '*.pyc' \
  "$PROJECT_ROOT/" "$APP_DIR/"

chown -R borsa:borsa "$APP_DIR"
success "Project copied to $APP_DIR"

# --------------------------------------------------------------------------- #
# 4. Python virtual environment + dependencies
# --------------------------------------------------------------------------- #
info "Creating Python virtual environment…"
python3.11 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install --quiet --upgrade pip wheel

info "Installing Python dependencies…"
"$APP_DIR/.venv/bin/pip" install --quiet \
  -r "$APP_DIR/application/backend/requirements.txt"
success "Python dependencies installed"

# --------------------------------------------------------------------------- #
# 5. Write production .env for the backend
# --------------------------------------------------------------------------- #
info "Writing backend .env…"
cat > "$APP_DIR/application/backend/.env" <<EOF
# ==========================================================
# BorsaTrust — Production Environment (auto-generated)
# Generated: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# ==========================================================

APP_ENV=production
APP_HOST=127.0.0.1
APP_PORT=$APP_PORT

DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASS
DB_SSLMODE=$DB_SSLMODE

SESSION_SECRET=$APP_SECRET
SESSION_COOKIE_SECURE=false
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=lax
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ORIGINS=$FRONTEND_ORIGIN
EOF
chmod 600 "$APP_DIR/application/backend/.env"
chown borsa:borsa "$APP_DIR/application/backend/.env"
success ".env written"

# --------------------------------------------------------------------------- #
# 6. Build the React frontend
# --------------------------------------------------------------------------- #
info "Installing frontend Node.js dependencies…"
npm --prefix "$APP_DIR/application/frontend" install --silent

info "Building frontend (vite)…"
# VITE_API_BASE_URL is empty — nginx proxies /api to the backend on the same host
VITE_API_BASE_URL="" npm --prefix "$APP_DIR/application/frontend" run build
success "Frontend built → $APP_DIR/application/frontend/dist"

# --------------------------------------------------------------------------- #
# 7. Systemd service for the FastAPI backend
# --------------------------------------------------------------------------- #
info "Installing systemd service (borsa-backend)…"
cp "$SCRIPT_DIR/borsa-backend.service" /etc/systemd/system/borsa-backend.service

# Patch paths in service file
sed -i "s|__APP_DIR__|$APP_DIR|g" /etc/systemd/system/borsa-backend.service
sed -i "s|__APP_PORT__|$APP_PORT|g" /etc/systemd/system/borsa-backend.service

systemctl daemon-reload
systemctl enable borsa-backend
systemctl restart borsa-backend
sleep 2

if systemctl is-active --quiet borsa-backend; then
  success "borsa-backend service is running"
else
  warn "borsa-backend failed to start — check: journalctl -u borsa-backend -n 50"
fi

# --------------------------------------------------------------------------- #
# 8. Nginx configuration
# --------------------------------------------------------------------------- #
info "Configuring Nginx…"
cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/sites-available/borsa
ln -sf /etc/nginx/sites-available/borsa /etc/nginx/sites-enabled/borsa
rm -f /etc/nginx/sites-enabled/default   # remove default page

# Patch backend port in nginx config
sed -i "s|__APP_PORT__|$APP_PORT|g" /etc/nginx/sites-available/borsa
sed -i "s|__APP_DIR__|$APP_DIR|g"   /etc/nginx/sites-available/borsa

nginx -t
systemctl enable nginx
systemctl restart nginx
success "Nginx configured and running"

# --------------------------------------------------------------------------- #
# 9. UFW firewall
# --------------------------------------------------------------------------- #
info "Configuring firewall (UFW)…"
ufw --force enable
ufw allow ssh
ufw allow 'Nginx Full'
ufw reload
success "Firewall configured — HTTP/HTTPS open"

# --------------------------------------------------------------------------- #
# Done
# --------------------------------------------------------------------------- #
VM1_IP="$(get_first_ip)"
echo
echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  VM1 Application Server setup complete!${NC}"
echo -e "${GREEN}============================================================${NC}"
echo
echo "  Frontend : http://$VM1_IP"
echo "  Backend  : http://$VM1_IP/api  (proxied by Nginx)"
echo "  Service  : systemctl status borsa-backend"
echo "  Logs     : journalctl -u borsa-backend -f"
echo
echo -e "${YELLOW}  Test credentials:${NC}"
echo "    alice   / alice1234   (customer)"
echo "    bob     / bob1234     (customer)"
echo "    charlie / charlie1234 (customer)"
echo "    admin   / adminpass1  (admin)"
echo
echo -e "${YELLOW}  To redeploy after code changes:${NC}"
echo "    sudo bash $SCRIPT_DIR/deploy.sh"
echo


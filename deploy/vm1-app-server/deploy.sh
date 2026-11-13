#!/usr/bin/env bash
# =============================================================================
# VM1 — Redeploy Script (after code changes)
# =============================================================================
# Syncs updated code from the project directory to /opt/borsa,
# rebuilds the frontend, restarts the backend service.
#
# Run as : sudo bash deploy.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
APP_DIR="/opt/borsa"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; NC='\033[0m'
info()    { echo -e "${CYAN}[INFO]${NC} $*"; }
success() { echo -e "${GREEN}[OK]${NC}   $*"; }
die()     { echo -e "${RED}[FAIL]${NC} $*" >&2; exit 1; }

[[ $EUID -eq 0 ]] || die "Run with: sudo bash $0"
[[ -d "$APP_DIR" ]] || die "App dir $APP_DIR not found — run setup.sh first"

info "=== BorsaTrust — Redeployment ==="

# 1. Sync source (preserve .env and .venv)
info "Syncing source code…"
rsync -a --delete \
  --exclude '.venv' \
  --exclude 'node_modules' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude 'dist' \
  --exclude '*.pyc' \
  --exclude '.env' \
  "$PROJECT_ROOT/" "$APP_DIR/"
chown -R borsa:borsa "$APP_DIR"
success "Source synced"

# 2. Update Python dependencies
info "Updating Python dependencies…"
"$APP_DIR/.venv/bin/pip" install --quiet --upgrade \
  -r "$APP_DIR/application/backend/requirements.txt"
success "Python deps updated"

# 3. Rebuild frontend
info "Rebuilding frontend…"
npm --prefix "$APP_DIR/application/frontend" install --silent
VITE_API_BASE_URL="" npm --prefix "$APP_DIR/application/frontend" run build
chown -R borsa:borsa "$APP_DIR"
success "Frontend rebuilt"

# 4. Restart backend
info "Restarting borsa-backend service…"
systemctl restart borsa-backend
sleep 2
systemctl is-active --quiet borsa-backend && success "Service restarted" || \
  { echo "Service failed — run: journalctl -u borsa-backend -n 50"; exit 1; }

success "=== Redeployment complete ==="


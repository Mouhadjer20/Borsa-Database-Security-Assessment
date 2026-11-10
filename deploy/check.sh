#!/usr/bin/env bash
# =============================================================================
# deploy/check.sh — Health Check (run from either VM or your host machine)
# =============================================================================
# Tests that the backend API and frontend are reachable and working.
# Usage : bash check.sh <VM1_IP>
# Example: bash check.sh 192.168.1.5
# =============================================================================
set -euo pipefail

VM1_IP="${1:-localhost}"
BASE="http://$VM1_IP"
PASS=0; FAIL=0

GREEN='\033[0;32m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
ok()   { echo -e "${GREEN}  ✓${NC} $*"; ((PASS++)); }
fail() { echo -e "${RED}  ✗${NC} $*"; ((FAIL++)); }

echo -e "${CYAN}=== BorsaTrust Health Check — $BASE ===${NC}"
echo

# Health endpoint
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/api/health" 2>/dev/null || echo "000")
[[ "$STATUS" == "200" ]] && ok "GET /api/health → 200" || fail "GET /api/health → $STATUS"

# Frontend index
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE/" 2>/dev/null || echo "000")
[[ "$STATUS" == "200" ]] && ok "GET / (frontend) → 200" || fail "GET / (frontend) → $STATUS"

# Login returns 401 (not 500 — backend is running)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"nobody","password":"wrong"}' 2>/dev/null || echo "000")
[[ "$STATUS" == "401" ]] && ok "POST /api/auth/login (bad creds) → 401" || fail "POST /api/auth/login → $STATUS (expected 401)"

# CTF endpoints exist
for ENDPOINT in "/api/auth/search?q=test" "/api/diagnostics/db-ping?host=127.0.0.1&port=5432"; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE$ENDPOINT" 2>/dev/null || echo "000")
  [[ "$STATUS" == "401" || "$STATUS" == "200" ]] && \
    ok "GET $ENDPOINT → $STATUS (endpoint exists)" || \
    fail "GET $ENDPOINT → $STATUS"
done

echo
echo "Result: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && echo -e "${GREEN}All checks passed ✓${NC}" && exit 0 || exit 1


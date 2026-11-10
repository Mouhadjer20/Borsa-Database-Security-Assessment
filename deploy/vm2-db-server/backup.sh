#!/usr/bin/env bash
# =============================================================================
# VM2 — Database Backup Script
# =============================================================================
# Creates a compressed pg_dump to /var/backups/borsa/
# Schedule with cron: 0 2 * * * /opt/borsa-deploy/vm2-db-server/backup.sh
# =============================================================================
set -euo pipefail

DB_NAME="borsa_db"
BACKUP_DIR="/var/backups/borsa"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/borsa_${TIMESTAMP}.sql.gz"
KEEP_DAYS=7

mkdir -p "$BACKUP_DIR"
chmod 750 "$BACKUP_DIR"

echo "[$(date)] Starting backup → $BACKUP_FILE"
sudo -u postgres pg_dump "$DB_NAME" | gzip > "$BACKUP_FILE"
echo "[$(date)] Backup complete: $(du -sh "$BACKUP_FILE" | cut -f1)"

# Remove backups older than KEEP_DAYS
find "$BACKUP_DIR" -name "borsa_*.sql.gz" -mtime "+$KEEP_DAYS" -delete
echo "[$(date)] Old backups cleaned (>${KEEP_DAYS} days)"


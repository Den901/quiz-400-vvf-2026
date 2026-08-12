#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/backups"
STAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "${BACKUP_DIR}"
cd "${PROJECT_DIR}"
docker compose --env-file cloud/.env -f cloud/compose.yml exec -T database \
  pg_dump -U quiz400 -d quiz400 -Fc > "${BACKUP_DIR}/quiz400-${STAMP}.dump"
find "${BACKUP_DIR}" -type f -name 'quiz400-*.dump' -mtime +30 -delete
echo "Backup creato: ${BACKUP_DIR}/quiz400-${STAMP}.dump"

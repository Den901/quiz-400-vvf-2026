#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_DIR}"
./cloud/backup-linux.sh
git pull --ff-only
docker compose --env-file cloud/.env -f cloud/compose.yml up -d --build
echo "Aggiornamento completato. Il database e i volumi sono stati conservati."

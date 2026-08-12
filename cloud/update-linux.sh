#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_DIR}"
./cloud/backup-linux.sh
git pull --ff-only

ENV_FILE="cloud/.env"
ensure_env_value() {
  local key="$1" value="$2"
  if ! grep -qE "^${key}=" "${ENV_FILE}"; then
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}
port_in_use() {
  local port="$1"
  { ss -H -ltn; ss -H -lun; } | awk '{print $4}' | grep -Eq "(^|:|\\])${port}$"
}

if ! grep -qE '^APP_PORT=' "${ENV_FILE}"; then
  if ! command -v ss >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y iproute2
  fi
  candidate=8088
  while port_in_use "${candidate}"; do
    candidate=$((candidate + 1))
  done
  ensure_env_value APP_PORT "${candidate}"
  ensure_env_value APP_BIND_ADDRESS 127.0.0.1
  ensure_env_value PROXY_MODE bundled
  ensure_env_value COMPOSE_PROFILES bundled-proxy
  ensure_env_value HTTP_PORT 80
  ensure_env_value HTTPS_PORT 443
  echo "Porta interna libera selezionata automaticamente: ${candidate}."
fi

docker compose --env-file cloud/.env -f cloud/compose.yml up -d --build
echo "Aggiornamento completato. Il database e i volumi sono stati conservati."

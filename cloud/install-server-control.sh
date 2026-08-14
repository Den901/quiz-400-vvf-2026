#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Esegui con sudo: sudo ./cloud/install-server-control.sh" >&2
  exit 1
fi
if [[ ! -f "${ENV_FILE}" || "${PROJECT_DIR}" == "/" ]]; then
  echo "Installazione Cloud non trovata." >&2
  exit 1
fi

set_env() {
  local key="$1" value="$2"
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    sed -i -E "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

install -d -o 10001 -g 10001 -m 0750 "${SCRIPT_DIR}/control" "${SCRIPT_DIR}/control/uploads"
install -o root -g root -m 0750 "${SCRIPT_DIR}/apply-server-request.sh" /usr/local/sbin/quiz400-apply-server-request
set_env PORT_CONTROL_CONTAINER_DIR /srv/quiz400-control

cat > /etc/systemd/system/quiz400-server-control.service <<EOF
[Unit]
Description=Aggiornamenti e controllo del portale Quiz 400 VVF 2026
After=docker.service network-online.target
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/quiz400-apply-server-request ${PROJECT_DIR}
TimeoutStartSec=20min
EOF

cat > /etc/systemd/system/quiz400-server-control.path <<EOF
[Unit]
Description=Sorveglia le richieste amministrative di Quiz 400 VVF 2026

[Path]
PathExists=${SCRIPT_DIR}/control/server-request.json
Unit=quiz400-server-control.service

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now quiz400-server-control.path
cd "${PROJECT_DIR}"
docker compose --env-file cloud/.env -f cloud/compose.yml up -d --no-build --force-recreate app
echo "Controllo aggiornamenti, riavvio e arresto installato."

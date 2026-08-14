#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
DOMAIN="${1:-}"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Esegui con sudo: sudo ./cloud/install-port-control.sh dominio.duckdns.org" >&2
  exit 1
fi
if [[ -z "${DOMAIN}" || ! "${DOMAIN}" =~ ^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$ ]]; then
  echo "Indica un dominio valido, per esempio quizvvf.duckdns.org" >&2
  exit 1
fi
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Installazione Cloud non trovata." >&2
  exit 1
fi
if [[ "${PROJECT_DIR}" =~ [[:space:]] ]]; then
  echo "Il percorso del progetto non deve contenere spazi." >&2
  exit 1
fi
if ! command -v caddy >/dev/null || ! systemctl is-active --quiet caddy; then
  echo "Il controllo diretto richiede Caddy attivo sul sistema host." >&2
  exit 1
fi

read_env() {
  local key="$1" fallback="$2" line
  line="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n1 || true)"
  [[ -n "${line}" ]] && printf '%s' "${line#*=}" || printf '%s' "${fallback}"
}
set_env() {
  local key="$1" value="$2"
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    sed -i -E "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

APP_PORT="$(read_env APP_PORT 8088)"
PROXY_MODE="$(read_env PROXY_MODE external)"
BIND_ADDRESS="$(read_env APP_BIND_ADDRESS 127.0.0.1)"
[[ "${APP_PORT}" =~ ^[0-9]+$ ]] || { echo "Porta app non valida." >&2; exit 1; }
[[ "${PROXY_MODE}" == "external" && "${BIND_ADDRESS}" == "127.0.0.1" ]] || {
  echo "Configura prima reverse proxy esterno con backend 127.0.0.1." >&2
  exit 1
}

install -d -o 10001 -g 10001 -m 0750 "${SCRIPT_DIR}/control"
install -o root -g root -m 0750 "${SCRIPT_DIR}/apply-port-request.sh" /usr/local/sbin/quiz400-apply-port-request
set_env PORT_CONTROL_CONTAINER_DIR /srv/quiz400-control
set_env PORT_CONTROL_CADDY_SNIPPET /etc/caddy/quiz400.caddy

CADDYFILE=/etc/caddy/Caddyfile
CADDY_SNIPPET=/etc/caddy/quiz400.caddy
cp -p "${CADDYFILE}" "${CADDYFILE}.quiz400-backup"
cat > "${CADDY_SNIPPET}" <<EOF
${DOMAIN} {
    encode gzip
    reverse_proxy 127.0.0.1:${APP_PORT}
}
EOF
chmod 0644 "${CADDY_SNIPPET}"
if ! grep -Fqx 'import /etc/caddy/quiz400.caddy' "${CADDYFILE}"; then
  printf '\n# Quiz 400 VVF 2026 - configurazione gestita\nimport /etc/caddy/quiz400.caddy\n' >> "${CADDYFILE}"
fi
if ! caddy validate --config "${CADDYFILE}"; then
  cp -p "${CADDYFILE}.quiz400-backup" "${CADDYFILE}"
  rm -f "${CADDY_SNIPPET}"
  echo "Configurazione Caddy non valida: ripristinata." >&2
  exit 1
fi
systemctl reload caddy

cat > /etc/systemd/system/quiz400-port-control.service <<EOF
[Unit]
Description=Applica in sicurezza il cambio porta di Quiz 400 VVF 2026
After=docker.service caddy.service
Requires=docker.service caddy.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/quiz400-apply-port-request ${PROJECT_DIR}
EOF

cat > /etc/systemd/system/quiz400-port-control.path <<EOF
[Unit]
Description=Sorveglia le richieste di cambio porta di Quiz 400 VVF 2026

[Path]
PathExists=${SCRIPT_DIR}/control/request.json
Unit=quiz400-port-control.service

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now quiz400-port-control.path
cd "${PROJECT_DIR}"
docker compose --env-file cloud/.env -f cloud/compose.yml up -d --build --force-recreate app
"${SCRIPT_DIR}/install-server-control.sh"
echo "Pannello porte attivo: HTTPS 443 -> backend locale ${APP_PORT}."

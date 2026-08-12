#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-}"
if [[ "$(id -u)" -ne 0 || -z "${PROJECT_DIR}" || ! -f "${PROJECT_DIR}/cloud/compose.yml" ]]; then
  echo "Uso: root quiz400-apply-port-request /percorso/progetto" >&2
  exit 2
fi

CONTROL_DIR="${PROJECT_DIR}/cloud/control"
REQUEST_FILE="${CONTROL_DIR}/request.json"
PROCESSING_FILE="${CONTROL_DIR}/request.processing.json"
STATUS_FILE="${CONTROL_DIR}/status.json"
ENV_FILE="${PROJECT_DIR}/cloud/.env"
COMPOSE=(docker compose --env-file cloud/.env -f cloud/compose.yml)

mkdir -p "${CONTROL_DIR}"
exec 9>"${CONTROL_DIR}/apply.lock"
flock -n 9 || exit 0
[[ -f "${REQUEST_FILE}" ]] || exit 0
mv -f "${REQUEST_FILE}" "${PROCESSING_FILE}"

write_status() {
  local state="$1" port="${2:-}" message="${3:-}" request_id="${4:-}"
  python3 - "${STATUS_FILE}" "${state}" "${port}" "${message}" "${request_id}" <<'PY'
import json, os, sys
from datetime import datetime, timezone
path, state, port, message, request_id = sys.argv[1:]
payload = {"state": state, "at": datetime.now(timezone.utc).isoformat()}
if port:
    payload["port"] = int(port)
if message:
    payload["message"] = message
if request_id:
    payload["requestId"] = request_id
temporary = path + ".tmp"
with open(temporary, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, ensure_ascii=False)
os.replace(temporary, path)
PY
  chown 10001:10001 "${STATUS_FILE}" 2>/dev/null || true
  chmod 0640 "${STATUS_FILE}" 2>/dev/null || true
}

read_env() {
  local key="$1" fallback="$2" line
  line="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n1 || true)"
  [[ -n "${line}" ]] && printf '%s' "${line#*=}" || printf '%s' "${fallback}"
}

set_env() {
  local key="$1" value="$2"
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    sed -i -E "s/^${key}=.*/${key}=${value}/" "${ENV_FILE}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

request_values="$(python3 - "${PROCESSING_FILE}" <<'PY'
import json, re, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    item = json.load(handle)
request_id = str(item.get("requestId", ""))
current = int(item.get("currentPort", 0))
target = int(item.get("appPort", 0))
domain = str(item.get("domain", "")).lower()
if not request_id or not 1024 <= current <= 65535 or not 1024 <= target <= 65535:
    raise SystemExit("Richiesta porta non valida")
if not re.fullmatch(r"[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?", domain):
    raise SystemExit("Dominio non valido")
print(request_id, current, target, domain)
PY
)" || {
  write_status error "" "Richiesta non valida."
  rm -f "${PROCESSING_FILE}"
  exit 1
}
read -r REQUEST_ID REQUEST_CURRENT_PORT NEW_PORT DOMAIN <<<"${request_values}"

OLD_PORT="$(read_env APP_PORT 8088)"
PROXY_MODE="$(read_env PROXY_MODE external)"
BIND_ADDRESS="$(read_env APP_BIND_ADDRESS 127.0.0.1)"
CADDY_SNIPPET="$(read_env PORT_CONTROL_CADDY_SNIPPET /etc/caddy/quiz400.caddy)"

fail_cleanly() {
  write_status error "${NEW_PORT}" "$1" "${REQUEST_ID}"
  rm -f "${PROCESSING_FILE}"
  exit 1
}

[[ "${OLD_PORT}" == "${REQUEST_CURRENT_PORT}" ]] || fail_cleanly "La porta attiva è cambiata: ricarica il pannello e riprova."
[[ "${PROXY_MODE}" == "external" && "${BIND_ADDRESS}" == "127.0.0.1" ]] || fail_cleanly "Il controllo protetto richiede reverse proxy esterno e backend locale."
if ss -H -ltn | awk '{print $4}' | grep -Eq "(^|:|\\])${NEW_PORT}$"; then
  fail_cleanly "La porta ${NEW_PORT} è già utilizzata."
fi

ENV_BACKUP="${ENV_FILE}.port-control-backup"
CADDY_BACKUP="${CADDY_SNIPPET}.port-control-backup"
cp -p "${ENV_FILE}" "${ENV_BACKUP}"
[[ -f "${CADDY_SNIPPET}" ]] && cp -p "${CADDY_SNIPPET}" "${CADDY_BACKUP}"
write_status applying "${NEW_PORT}" "Riavvio del backend e aggiornamento di Caddy." "${REQUEST_ID}"

rollback() {
  set +e
  cp -p "${ENV_BACKUP}" "${ENV_FILE}"
  cd "${PROJECT_DIR}"
  "${COMPOSE[@]}" up -d --force-recreate app >/dev/null 2>&1
  if [[ -f "${CADDY_BACKUP}" ]]; then
    cp -p "${CADDY_BACKUP}" "${CADDY_SNIPPET}"
    caddy validate --config /etc/caddy/Caddyfile >/dev/null 2>&1 && systemctl reload caddy
  fi
  write_status error "${NEW_PORT}" "Cambio non riuscito; porta ${OLD_PORT} ripristinata." "${REQUEST_ID}"
  rm -f "${PROCESSING_FILE}" "${ENV_BACKUP}" "${CADDY_BACKUP}"
}
trap 'rollback; exit 1' ERR

set_env APP_PORT "${NEW_PORT}"
cd "${PROJECT_DIR}"
"${COMPOSE[@]}" up -d --force-recreate app

healthy=0
for _ in $(seq 1 45); do
  if curl -fsS --max-time 3 "http://127.0.0.1:${NEW_PORT}/api/health" >/dev/null; then
    healthy=1
    break
  fi
  sleep 2
done
[[ "${healthy}" == "1" ]]

cat > "${CADDY_SNIPPET}.tmp" <<EOF
${DOMAIN} {
    encode gzip
    reverse_proxy 127.0.0.1:${NEW_PORT}
}
EOF
chmod 0644 "${CADDY_SNIPPET}.tmp"
mv -f "${CADDY_SNIPPET}.tmp" "${CADDY_SNIPPET}"
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy

trap - ERR
write_status applied "${NEW_PORT}" "Porta backend aggiornata; HTTPS pubblico invariato sulla 443." "${REQUEST_ID}"
rm -f "${PROCESSING_FILE}" "${ENV_BACKUP}" "${CADDY_BACKUP}"

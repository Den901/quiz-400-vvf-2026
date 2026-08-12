#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
COMPOSE=(docker compose --env-file cloud/.env -f cloud/compose.yml)

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Esegui con sudo: sudo ./cloud/configure-ports.sh"
  exit 1
fi
if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Installazione non trovata: esegui prima sudo ./cloud/install-linux.sh"
  exit 1
fi
if ! command -v ss >/dev/null 2>&1; then
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y iproute2
fi

read_env() {
  local key="$1" fallback="$2" line
  line="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n1 || true)"
  if [[ -n "${line}" ]]; then
    printf '%s' "${line#*=}"
  else
    printf '%s' "${fallback}"
  fi
}

port_in_use() {
  local port="$1"
  { ss -H -ltn; ss -H -lun; } | awk '{print $4}' | grep -Eq "(^|:|\\])${port}$"
}

choose_port() {
  local label="$1" current="$2" allow_current="${3:-true}" candidate
  while true; do
    read -r -p "Porta ${label} [${current}]: " candidate
    candidate="${candidate:-${current}}"
    if [[ ! "${candidate}" =~ ^[0-9]+$ ]] || (( candidate < 1 || candidate > 65535 )); then
      echo "Inserisci una porta valida tra 1 e 65535."
      continue
    fi
    if port_in_use "${candidate}" && { [[ "${candidate}" != "${current}" ]] || [[ "${allow_current}" != "true" ]]; }; then
      echo "La porta ${candidate} è già utilizzata. Scegline un'altra."
      continue
    fi
    SELECTED_PORT="${candidate}"
    return
  done
}

set_env() {
  local key="$1" value="$2"
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    sed -i -E "s/^${key}=.*/${key}=${value}/" "${ENV_FILE}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

OLD_PROXY_MODE="$(read_env PROXY_MODE bundled)"
OLD_APP_PORT="$(read_env APP_PORT 8088)"
OLD_BIND_ADDRESS="$(read_env APP_BIND_ADDRESS 127.0.0.1)"
OLD_HTTP_PORT="$(read_env HTTP_PORT 80)"
OLD_HTTPS_PORT="$(read_env HTTPS_PORT 443)"
OLD_COMPOSE_PROFILES="$(read_env COMPOSE_PROFILES bundled-proxy)"

echo "Modalità attuale: ${OLD_PROXY_MODE}; backend ${OLD_BIND_ADDRESS}:${OLD_APP_PORT}."
if [[ "${OLD_PROXY_MODE}" == "external" ]]; then
  read -r -p "Usi un reverse proxy HTTPS già esistente? [S/n]: " USE_EXISTING_PROXY
  USE_EXISTING_PROXY="${USE_EXISTING_PROXY:-s}"
else
  read -r -p "Usi un reverse proxy HTTPS già esistente? [s/N]: " USE_EXISTING_PROXY
  USE_EXISTING_PROXY="${USE_EXISTING_PROXY:-n}"
fi
choose_port "interna dell'app" "${OLD_APP_PORT}"
NEW_APP_PORT="${SELECTED_PORT}"

case "${USE_EXISTING_PROXY:-n}" in
  s|S|si|SI|sì|SÌ)
    NEW_PROXY_MODE="external"
    NEW_COMPOSE_PROFILES=""
    NEW_HTTP_PORT="${OLD_HTTP_PORT}"
    NEW_HTTPS_PORT="${OLD_HTTPS_PORT}"
    read -r -p "Il reverse proxy gira direttamente sul sistema host? [S/n]: " PROXY_ON_HOST
    case "${PROXY_ON_HOST:-s}" in
      n|N|no|NO) NEW_BIND_ADDRESS="0.0.0.0" ;;
      *) NEW_BIND_ADDRESS="127.0.0.1" ;;
    esac
    ;;
  *)
    NEW_PROXY_MODE="bundled"
    NEW_COMPOSE_PROFILES="bundled-proxy"
    NEW_BIND_ADDRESS="127.0.0.1"
    ALLOW_PUBLIC_CURRENT="false"
    if [[ "${OLD_PROXY_MODE}" == "bundled" ]]; then
      ALLOW_PUBLIC_CURRENT="true"
    fi
    while true; do
      choose_port "HTTP pubblica" "${OLD_HTTP_PORT}" "${ALLOW_PUBLIC_CURRENT}"
      NEW_HTTP_PORT="${SELECTED_PORT}"
      if [[ "${NEW_HTTP_PORT}" == "${NEW_APP_PORT}" ]]; then
        echo "La porta HTTP deve essere diversa dalla porta interna dell'app."
        continue
      fi
      break
    done
    while true; do
      choose_port "HTTPS pubblica" "${OLD_HTTPS_PORT}" "${ALLOW_PUBLIC_CURRENT}"
      NEW_HTTPS_PORT="${SELECTED_PORT}"
      if [[ "${NEW_HTTPS_PORT}" == "${NEW_HTTP_PORT}" || "${NEW_HTTPS_PORT}" == "${NEW_APP_PORT}" ]]; then
        echo "HTTP, HTTPS e app devono usare porte diverse."
        continue
      fi
      break
    done
    ;;
esac

set_env PROXY_MODE "${NEW_PROXY_MODE}"
set_env COMPOSE_PROFILES "${NEW_COMPOSE_PROFILES}"
set_env APP_PORT "${NEW_APP_PORT}"
set_env APP_BIND_ADDRESS "${NEW_BIND_ADDRESS}"
set_env HTTP_PORT "${NEW_HTTP_PORT}"
set_env HTTPS_PORT "${NEW_HTTPS_PORT}"

cd "${PROJECT_DIR}"
apply_failed=0
if [[ "${NEW_PROXY_MODE}" == "external" ]]; then
  "${COMPOSE[@]}" --profile bundled-proxy stop caddy || true
  "${COMPOSE[@]}" up -d --force-recreate app || apply_failed=1
else
  "${COMPOSE[@]}" --profile bundled-proxy up -d --force-recreate app caddy || apply_failed=1
fi

if (( apply_failed )); then
  echo "Cambio non riuscito: ripristino la configurazione precedente."
  set_env PROXY_MODE "${OLD_PROXY_MODE}"
  set_env COMPOSE_PROFILES "${OLD_COMPOSE_PROFILES}"
  set_env APP_PORT "${OLD_APP_PORT}"
  set_env APP_BIND_ADDRESS "${OLD_BIND_ADDRESS}"
  set_env HTTP_PORT "${OLD_HTTP_PORT}"
  set_env HTTPS_PORT "${OLD_HTTPS_PORT}"
  if [[ "${OLD_PROXY_MODE}" == "external" ]]; then
    "${COMPOSE[@]}" up -d --force-recreate app
  else
    "${COMPOSE[@]}" --profile bundled-proxy up -d --force-recreate app caddy
  fi
  exit 1
fi

if [[ "${NEW_PROXY_MODE}" == "external" ]]; then
  echo "Configurazione completata: il pubblico continua a usare HTTPS sulla porta 443 del reverse proxy."
  echo "Backend da impostare nel reverse proxy: http://${NEW_BIND_ADDRESS}:${NEW_APP_PORT}"
  echo "Inoltra Host, X-Forwarded-For e X-Forwarded-Proto=https."
else
  echo "Proxy incluso attivo: HTTP ${NEW_HTTP_PORT}, HTTPS ${NEW_HTTPS_PORT}."
fi

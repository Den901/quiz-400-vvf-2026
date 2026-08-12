#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Esegui questo installatore con sudo: sudo ./cloud/install-linux.sh"
  exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
  if ! command -v apt-get >/dev/null 2>&1 || [[ ! -r /etc/os-release ]]; then
    echo "Installazione automatica supportata solo su Ubuntu e Debian."
    exit 1
  fi
  . /etc/os-release
  case "${ID:-}" in
    ubuntu|debian) ;;
    *) echo "Distribuzione non supportata automaticamente: ${ID:-sconosciuta}."; exit 1 ;;
  esac
  echo "Docker non trovato: configurazione del repository ufficiale Docker..."
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl gnupg openssl
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/${ID}/gpg" -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  ARCHITECTURE="$(dpkg --print-architecture)"
  CODENAME="${VERSION_CODENAME:-}"
  if [[ -z "${CODENAME}" ]]; then
    echo "Impossibile rilevare la versione della distribuzione."
    exit 1
  fi
  printf 'deb [arch=%s signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/%s %s stable\n' "${ARCHITECTURE}" "${ID}" "${CODENAME}" > /etc/apt/sources.list.d/docker.list
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Il plugin Docker Compose non è disponibile. Installalo e rilancia lo script."
  exit 1
fi

if ! command -v openssl >/dev/null 2>&1 || ! command -v ss >/dev/null 2>&1; then
  if command -v apt-get >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y openssl iproute2
  else
    echo "Servono openssl e il comando ss per completare l'installazione."
    exit 1
  fi
fi

port_in_use() {
  local port="$1"
  { ss -H -ltn; ss -H -lun; } | awk '{print $4}' | grep -Eq "(^|:|\\])${port}$"
}

choose_available_port() {
  local label="$1" default_port="$2" candidate
  while true; do
    read -r -p "Porta ${label} [${default_port}]: " candidate
    candidate="${candidate:-${default_port}}"
    if [[ ! "${candidate}" =~ ^[0-9]+$ ]] || (( candidate < 1 || candidate > 65535 )); then
      echo "Inserisci una porta valida tra 1 e 65535."
      continue
    fi
    if port_in_use "${candidate}"; then
      echo "La porta ${candidate} è già utilizzata. Scegline un'altra."
      continue
    fi
    SELECTED_PORT="${candidate}"
    return
  done
}

ensure_env_value() {
  local key="$1" value="$2"
  if ! grep -qE "^${key}=" "${ENV_FILE}"; then
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

if [[ ! -f "${ENV_FILE}" ]]; then
  read -r -p "Nome utente amministratore [admin]: " ADMIN_USERNAME
  ADMIN_USERNAME="${ADMIN_USERNAME:-admin}"
  if [[ ! "${ADMIN_USERNAME}" =~ ^[A-Za-z0-9._-]{3,40}$ ]]; then
    echo "Il nome utente deve avere 3-40 caratteri: lettere, numeri, punto, trattino o trattino basso."
    exit 1
  fi
  read -r -p "Nome visualizzato [Amministratore]: " ADMIN_NAME
  ADMIN_NAME="${ADMIN_NAME:-Amministratore}"
  read -r -p "Email amministratore (facoltativa): " ADMIN_EMAIL
  read -r -s -p "Password amministratore (almeno 10 caratteri): " ADMIN_PASSWORD
  echo
  if [[ ${#ADMIN_PASSWORD} -lt 10 ]]; then
    echo "La password deve avere almeno 10 caratteri."
    exit 1
  fi
  if [[ ! "${ADMIN_PASSWORD}" =~ ^[A-Za-z0-9._!@%+=,:/-]+$ ]]; then
    echo "Per l'installazione iniziale usa lettere, numeri e i simboli . _ ! @ % + = , : / -"
    exit 1
  fi
  echo
  echo "Configurazione rete e controllo porte..."
  read -r -p "Usi già un reverse proxy HTTPS su questo server? [s/N]: " USE_EXISTING_PROXY
  choose_available_port "interna dell'app" "8088"
  APP_PORT="${SELECTED_PORT}"
  HTTP_PORT="80"
  HTTPS_PORT="443"
  case "${USE_EXISTING_PROXY:-n}" in
    s|S|si|SI|sì|SÌ)
      PROXY_MODE="external"
      COMPOSE_PROFILES=""
      read -r -p "Il reverse proxy gira direttamente sul sistema host? [S/n]: " PROXY_ON_HOST
      case "${PROXY_ON_HOST:-s}" in
        n|N|no|NO) APP_BIND_ADDRESS="0.0.0.0" ;;
        *) APP_BIND_ADDRESS="127.0.0.1" ;;
      esac
      ;;
    *)
      PROXY_MODE="bundled"
      COMPOSE_PROFILES="bundled-proxy"
      APP_BIND_ADDRESS="127.0.0.1"
      while true; do
        choose_available_port "HTTP pubblica" "80"
        HTTP_PORT="${SELECTED_PORT}"
        if [[ "${HTTP_PORT}" == "${APP_PORT}" ]]; then
          echo "La porta HTTP deve essere diversa dalla porta interna dell'app."
          continue
        fi
        break
      done
      while true; do
        choose_available_port "HTTPS pubblica" "443"
        HTTPS_PORT="${SELECTED_PORT}"
        if [[ "${HTTPS_PORT}" == "${HTTP_PORT}" || "${HTTPS_PORT}" == "${APP_PORT}" ]]; then
          echo "HTTP, HTTPS e app devono usare porte diverse."
          continue
        fi
        break
      done
      ;;
  esac
  POSTGRES_PASSWORD="$(openssl rand -hex 32)"
  APP_SECRET="$(openssl rand -hex 48)"
  umask 077
  {
    printf 'POSTGRES_PASSWORD=%s\n' "${POSTGRES_PASSWORD}"
    printf 'APP_SECRET=%s\n' "${APP_SECRET}"
    printf 'ADMIN_USERNAME=%s\n' "${ADMIN_USERNAME}"
    printf 'ADMIN_NAME=%s\n' "${ADMIN_NAME}"
    printf 'ADMIN_EMAIL=%s\n' "${ADMIN_EMAIL}"
    printf 'ADMIN_PASSWORD=%s\n' "${ADMIN_PASSWORD}"
    printf 'HTTP_PORT=%s\n' "${HTTP_PORT}"
    printf 'HTTPS_PORT=%s\n' "${HTTPS_PORT}"
    printf 'APP_PORT=%s\n' "${APP_PORT}"
    printf 'APP_BIND_ADDRESS=%s\n' "${APP_BIND_ADDRESS}"
    printf 'PROXY_MODE=%s\n' "${PROXY_MODE}"
    printf 'COMPOSE_PROFILES=%s\n' "${COMPOSE_PROFILES}"
  } > "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
  echo "Configurazione protetta creata in cloud/.env"
fi

if ! grep -qE '^APP_PORT=' "${ENV_FILE}"; then
  echo "Aggiornamento della configurazione rete esistente..."
  choose_available_port "interna dell'app" "8088"
  ensure_env_value HTTP_PORT 80
  ensure_env_value HTTPS_PORT 443
  ensure_env_value APP_PORT "${SELECTED_PORT}"
  ensure_env_value APP_BIND_ADDRESS 127.0.0.1
  ensure_env_value PROXY_MODE bundled
  ensure_env_value COMPOSE_PROFILES bundled-proxy
fi

cd "${PROJECT_DIR}"
docker compose --env-file cloud/.env -f cloud/compose.yml up -d --build

echo
echo "Quiz 400 VVF 2026 Cloud è avviato."
PROXY_MODE="$(grep -E '^PROXY_MODE=' cloud/.env | tail -n1 | cut -d= -f2- || true)"
APP_PORT="$(grep -E '^APP_PORT=' cloud/.env | tail -n1 | cut -d= -f2- || true)"
APP_BIND_ADDRESS="$(grep -E '^APP_BIND_ADDRESS=' cloud/.env | tail -n1 | cut -d= -f2- || true)"
HTTP_PORT="$(grep -E '^HTTP_PORT=' cloud/.env | tail -n1 | cut -d= -f2- || true)"
HTTPS_PORT="$(grep -E '^HTTPS_PORT=' cloud/.env | tail -n1 | cut -d= -f2- || true)"
PROXY_MODE="${PROXY_MODE:-bundled}"
APP_PORT="${APP_PORT:-8088}"
APP_BIND_ADDRESS="${APP_BIND_ADDRESS:-127.0.0.1}"
HTTP_PORT="${HTTP_PORT:-80}"
HTTPS_PORT="${HTTPS_PORT:-443}"
if [[ "${PROXY_MODE}" == "external" ]]; then
  echo "L'app è pronta per il reverse proxy su ${APP_BIND_ADDRESS}:${APP_PORT}."
  echo "Mantieni la porta pubblica 443 sul reverse proxy e inoltra al backend HTTP sulla porta ${APP_PORT}."
  echo "Configura il dominio HTTPS nel reverse proxy, poi apri https://TUO-DOMINIO."
else
  if [[ "${HTTP_PORT}" == "80" ]]; then
    echo "Apri http://IP-DEL-SERVER e accedi con l'amministratore creato."
  else
    echo "Apri http://IP-DEL-SERVER:${HTTP_PORT} e accedi con l'amministratore creato."
  fi
  echo "HTTPS è attivo sulla porta server ${HTTPS_PORT}."
  if [[ "${HTTP_PORT}" != "80" || "${HTTPS_PORT}" != "443" ]]; then
    echo "Sul router inoltra la porta pubblica 80 verso ${HTTP_PORT} e la 443 verso ${HTTPS_PORT}."
  fi
fi
echo "Dal pannello Impostazioni Cloud configura DuckDNS, URL pubblico e posta SMTP."
echo "Per cambiare le porte in seguito: sudo ./cloud/configure-ports.sh"

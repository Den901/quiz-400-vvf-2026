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
  } > "${ENV_FILE}"
  chmod 600 "${ENV_FILE}"
  echo "Configurazione protetta creata in cloud/.env"
fi

cd "${PROJECT_DIR}"
docker compose --env-file cloud/.env -f cloud/compose.yml up -d --build

echo
echo "Quiz 400 VVF 2026 Cloud è avviato."
echo "Apri http://IP-DEL-SERVER e accedi con l'amministratore creato."
echo "Dal pannello Impostazioni Cloud configura DuckDNS, URL pubblico e posta SMTP."

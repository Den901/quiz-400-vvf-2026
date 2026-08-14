#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${1:-}"
if [[ "$(id -u)" -ne 0 || -z "${PROJECT_DIR}" || "${PROJECT_DIR}" == "/" || ! -f "${PROJECT_DIR}/cloud/compose.yml" ]]; then
  echo "Uso: root quiz400-apply-server-request /percorso/progetto" >&2
  exit 2
fi

PROJECT_DIR="$(cd -- "${PROJECT_DIR}" && pwd)"
CONTROL_DIR="${PROJECT_DIR}/cloud/control"
REQUEST_FILE="${CONTROL_DIR}/server-request.json"
PROCESSING_FILE="${CONTROL_DIR}/server-request.processing.json"
STATUS_FILE="${CONTROL_DIR}/server-status.json"
ENV_FILE="${PROJECT_DIR}/cloud/.env"
COMPOSE=(docker compose --env-file cloud/.env -f cloud/compose.yml)

mkdir -p "${CONTROL_DIR}"
exec 9>"${CONTROL_DIR}/server-control.lock"
flock -n 9 || exit 0
[[ -f "${REQUEST_FILE}" ]] || exit 0
mv -f "${REQUEST_FILE}" "${PROCESSING_FILE}"

write_status() {
  local state="$1" message="${2:-}" request_id="${3:-}" version="${4:-}"
  python3 - "${STATUS_FILE}" "${state}" "${message}" "${request_id}" "${version}" <<'PY'
import json, os, sys
from datetime import datetime, timezone
path, state, message, request_id, version = sys.argv[1:]
payload = {"state": state, "at": datetime.now(timezone.utc).isoformat()}
if message:
    payload["message"] = message
if request_id:
    payload["requestId"] = request_id
if version:
    payload["version"] = version
temporary = path + ".tmp"
with open(temporary, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, ensure_ascii=False)
os.replace(temporary, path)
PY
  chown 10001:10001 "${STATUS_FILE}" 2>/dev/null || true
  chmod 0640 "${STATUS_FILE}" 2>/dev/null || true
}

mapfile -t REQUEST_VALUES < <(python3 - "${PROCESSING_FILE}" <<'PY'
import json, re, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    item = json.load(handle)
request_id = str(item.get("requestId", ""))
action = str(item.get("action", ""))
source = str(item.get("source", ""))
version = str(item.get("targetVersion", ""))
sha256 = str(item.get("sha256", ""))
asset_url = str(item.get("assetUrl", ""))
file_path = str(item.get("filePath", ""))
if not re.fullmatch(r"[0-9a-f-]{36}", request_id) or action not in {"update", "restart", "stop"}:
    raise SystemExit("Richiesta non valida")
if action == "update":
    if source not in {"github", "upload"} or not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", version):
        raise SystemExit("Aggiornamento non valido")
    if sha256 and not re.fullmatch(r"[0-9a-f]{64}", sha256):
        raise SystemExit("Hash non valido")
    if source == "github" and not re.fullmatch(r"https://github\.com/Den901/quiz-400-vvf-2026/releases/download/[^\s]+", asset_url):
        raise SystemExit("URL release non consentito")
    if source == "upload" and not re.fullmatch(r"uploads/update-[0-9a-f-]{36}\.zip", file_path):
        raise SystemExit("Percorso upload non valido")
for value in (request_id, action, source, version, sha256, asset_url, file_path):
    print(value)
PY
) || {
  write_status error "Richiesta del pannello non valida."
  rm -f "${PROCESSING_FILE}"
  exit 1
}

REQUEST_ID="${REQUEST_VALUES[0]:-}"
ACTION="${REQUEST_VALUES[1]:-}"
SOURCE="${REQUEST_VALUES[2]:-}"
TARGET_VERSION="${REQUEST_VALUES[3]:-}"
EXPECTED_SHA="${REQUEST_VALUES[4]:-}"
ASSET_URL="${REQUEST_VALUES[5]:-}"
FILE_PATH="${REQUEST_VALUES[6]:-}"

cd "${PROJECT_DIR}"

wait_until_healthy() {
  local port bind_address healthy=0
  port="$(grep -E '^APP_PORT=' "${ENV_FILE}" | tail -n1 | cut -d= -f2- || true)"
  bind_address="$(grep -E '^APP_BIND_ADDRESS=' "${ENV_FILE}" | tail -n1 | cut -d= -f2- || true)"
  port="${port:-8088}"
  [[ "${bind_address:-127.0.0.1}" == "0.0.0.0" ]] && bind_address="127.0.0.1"
  bind_address="${bind_address:-127.0.0.1}"
  for _ in $(seq 1 120); do
    if curl -fsS --max-time 3 "http://${bind_address}:${port}/api/health" >/dev/null 2>&1; then
      healthy=1
      break
    fi
    sleep 2
  done
  [[ "${healthy}" == "1" ]]
}

wait_until_version() {
  local expected="$1" port bind_address payload
  port="$(grep -E '^APP_PORT=' "${ENV_FILE}" | tail -n1 | cut -d= -f2- || true)"
  bind_address="$(grep -E '^APP_BIND_ADDRESS=' "${ENV_FILE}" | tail -n1 | cut -d= -f2- || true)"
  port="${port:-8088}"
  [[ "${bind_address:-127.0.0.1}" == "0.0.0.0" ]] && bind_address="127.0.0.1"
  bind_address="${bind_address:-127.0.0.1}"
  for _ in $(seq 1 120); do
    payload="$(curl -fsS --max-time 3 "http://${bind_address}:${port}/api/runtime" 2>/dev/null || true)"
    if [[ -n "${payload}" ]] && python3 - "${expected}" "${payload}" <<'PY'
import json, sys
raise SystemExit(0 if str(json.loads(sys.argv[2]).get("version")) == sys.argv[1] else 1)
PY
    then
      return 0
    fi
    sleep 2
  done
  return 1
}

if [[ "${ACTION}" == "restart" ]]; then
  write_status restarting "Riavvio del portale in corso." "${REQUEST_ID}"
  "${COMPOSE[@]}" up -d --no-build --force-recreate app
  if wait_until_healthy; then
    write_status completed "Portale riavviato correttamente." "${REQUEST_ID}"
    rm -f "${PROCESSING_FILE}"
    exit 0
  fi
  write_status error "Il portale non è tornato disponibile dopo il riavvio." "${REQUEST_ID}"
  rm -f "${PROCESSING_FILE}"
  exit 1
fi

if [[ "${ACTION}" == "stop" ]]; then
  write_status stopping "Arresto del solo portale in corso; il server resta acceso." "${REQUEST_ID}"
  "${COMPOSE[@]}" stop app
  write_status stopped "Portale arrestato. Per riaccenderlo usa cloud/start-linux.sh sul server." "${REQUEST_ID}"
  rm -f "${PROCESSING_FILE}"
  exit 0
fi

WORK_DIR="$(mktemp -d "${CONTROL_DIR}/server-update.XXXXXX")"
PACKAGE_FILE="${WORK_DIR}/update.zip"
STAGE_DIR="${WORK_DIR}/stage"
SOURCE_BACKUP="${PROJECT_DIR}/cloud/backups/source-before-${TARGET_VERSION}-$(date +%Y%m%d-%H%M%S).tar.gz"
CURRENT_VERSION="$(python3 -c 'import json; print(json.load(open("version.json", encoding="utf-8"))["version"])' 2>/dev/null || printf 'sconosciuta')"

cleanup() {
  rm -rf -- "${WORK_DIR}"
  rm -f "${PROCESSING_FILE}"
}
trap cleanup EXIT
trap 'write_status error "Download o verifica del pacchetto non riusciti." "${REQUEST_ID}" "${TARGET_VERSION}"' ERR

write_status downloading "Preparazione del pacchetto ${TARGET_VERSION}." "${REQUEST_ID}" "${TARGET_VERSION}"
if [[ "${SOURCE}" == "github" ]]; then
  curl --fail --location --silent --show-error --connect-timeout 20 --max-time 300 "${ASSET_URL}" --output "${PACKAGE_FILE}"
else
  UPLOAD_FILE="$(realpath -e -- "${CONTROL_DIR}/${FILE_PATH}")"
  case "${UPLOAD_FILE}" in
    "${CONTROL_DIR}"/uploads/update-*.zip) ;;
    *) write_status error "Percorso del pacchetto caricato non consentito." "${REQUEST_ID}" "${TARGET_VERSION}"; exit 1 ;;
  esac
  cp -- "${UPLOAD_FILE}" "${PACKAGE_FILE}"
fi

if [[ -n "${EXPECTED_SHA}" ]]; then
  ACTUAL_SHA="$(sha256sum "${PACKAGE_FILE}" | awk '{print $1}')"
  [[ "${ACTUAL_SHA}" == "${EXPECTED_SHA}" ]] || {
    write_status error "Il controllo di integrità del pacchetto non è riuscito." "${REQUEST_ID}" "${TARGET_VERSION}"
    exit 1
  }
fi

mkdir -p "${STAGE_DIR}" "${PROJECT_DIR}/cloud/backups"
python3 - "${PACKAGE_FILE}" "${STAGE_DIR}" "${TARGET_VERSION}" <<'PY'
import hashlib, json, os, shutil, stat, sys, zipfile
from pathlib import PurePosixPath

package, stage, expected_version = sys.argv[1:]
with zipfile.ZipFile(package) as archive:
    infos = {item.filename: item for item in archive.infolist()}
    if "release-manifest.json" not in infos or "version.json" not in infos:
        raise SystemExit("Manifest server mancante")
    manifest = json.loads(archive.read("release-manifest.json"))
    version_data = json.loads(archive.read("version.json"))
    if manifest.get("app") != "Quiz 400 VVF 2026 Server" or manifest.get("version") != expected_version or version_data.get("version") != expected_version:
        raise SystemExit("Versione o applicazione non corrispondente")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("Elenco file mancante")
    for item in files:
        path = str(item.get("path", "")).replace("\\", "/")
        pure = PurePosixPath(path)
        if not path or pure.is_absolute() or ".." in pure.parts or path not in infos:
            raise SystemExit("Percorso non sicuro nel manifest")
        info = infos[path]
        if stat.S_ISLNK(info.external_attr >> 16):
            raise SystemExit("Collegamenti simbolici non consentiti")
        content = archive.read(info)
        if hashlib.sha256(content).hexdigest() != item.get("sha256"):
            raise SystemExit(f"Hash file non valido: {path}")
        target = os.path.join(stage, *pure.parts)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as handle:
            handle.write(content)
    with open(os.path.join(stage, "release-manifest.json"), "wb") as handle:
        handle.write(archive.read("release-manifest.json"))
PY

write_status backing-up "Backup PostgreSQL e copia dei file correnti." "${REQUEST_ID}" "${TARGET_VERSION}"
"${PROJECT_DIR}/cloud/backup-linux.sh"
tar --exclude='./.git' --exclude='./cloud/.env' --exclude='./cloud/backups' --exclude='./cloud/control' --exclude='./cloud/data' --exclude='./tmp' -czf "${SOURCE_BACKUP}" -C "${PROJECT_DIR}" .

rollback_update() {
  set +e
  tar -xzf "${SOURCE_BACKUP}" -C "${PROJECT_DIR}"
  chmod +x "${PROJECT_DIR}"/cloud/*.sh 2>/dev/null || true
  cd "${PROJECT_DIR}"
  "${COMPOSE[@]}" up -d --build app >/dev/null 2>&1
  write_status error "Aggiornamento non riuscito; file della ${CURRENT_VERSION} ripristinati." "${REQUEST_ID}" "${CURRENT_VERSION}"
}
trap 'rollback_update; exit 1' ERR

write_status installing "Installazione ${TARGET_VERSION} e riavvio del portale." "${REQUEST_ID}" "${TARGET_VERSION}"
python3 - "${STAGE_DIR}" "${PROJECT_DIR}" <<'PY'
import json, os, shutil, sys
from pathlib import Path, PurePosixPath

stage = Path(sys.argv[1]).resolve()
project = Path(sys.argv[2]).resolve()
manifest = json.loads((stage / "release-manifest.json").read_text(encoding="utf-8"))
protected = {".git", "cloud/.env", "cloud/backups", "cloud/control", "cloud/data"}

def safe_relative(value):
    path = str(value).replace("\\", "/")
    pure = PurePosixPath(path)
    if not path or pure.is_absolute() or ".." in pure.parts:
        raise SystemExit("Percorso aggiornamento non sicuro")
    if path in protected or any(path.startswith(item + "/") for item in protected):
        raise SystemExit("Il pacchetto tenta di modificare dati protetti")
    return pure

for item in manifest["files"]:
    relative = safe_relative(item["path"])
    source = stage.joinpath(*relative.parts)
    target = project.joinpath(*relative.parts)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".update-tmp")
    shutil.copy2(source, temporary)
    os.replace(temporary, target)
for value in manifest.get("removedFiles", []):
    relative = safe_relative(value)
    target = project.joinpath(*relative.parts)
    if target.is_file() or target.is_symlink():
        target.unlink()
PY
chmod +x "${PROJECT_DIR}"/cloud/*.sh
install -o root -g root -m 0750 "${PROJECT_DIR}/cloud/apply-server-request.sh" /usr/local/sbin/quiz400-apply-server-request
"${COMPOSE[@]}" up -d --build app
wait_until_version "${TARGET_VERSION}"

trap - ERR
write_status completed "Versione ${TARGET_VERSION} installata correttamente. Backup conservati." "${REQUEST_ID}" "${TARGET_VERSION}"
if [[ "${SOURCE}" == "upload" ]]; then
  rm -f -- "${CONTROL_DIR}/${FILE_PATH}"
fi
find "${PROJECT_DIR}/cloud/backups" -type f -name 'source-before-*.tar.gz' -mtime +30 -delete

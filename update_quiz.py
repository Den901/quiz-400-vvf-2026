#!/usr/bin/env python3
"""Aggiorna Quiz 400 VVF 2026 preservando tutti i dati portatili."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

FROZEN = bool(getattr(sys, "frozen", False))
ROOT = (
    Path(sys.executable).resolve().parent
    if FROZEN
    else Path(__file__).resolve().parent
)
DATA_DIR = ROOT / "portable-data"
STATE_FILE = DATA_DIR / "fuocoquiz-state.json"
BACKUP_DIR = DATA_DIR / "backups"
VERSION_FILE = ROOT / "version.json"
REPOSITORY = "Den901/quiz-400-vvf-2026"
ASSET_NAME = (
    "Quiz-400-VVF-2026-Windows-EXE.zip"
    if FROZEN
    else "Quiz-400-VVF-2026-Portable.zip"
)
LATEST_API = f"https://api.github.com/repos/{REPOSITORY}/releases/latest"
PROTECTED_NAMES = {"portable-data", ".git", "outputs", "work", "tmp"}
if FROZEN:
    PROTECTED_NAMES.add(Path(sys.executable).name)


def request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Quiz-400-VVF-2026-Updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )


def current_version() -> str:
    try:
        return str(json.loads(VERSION_FILE.read_text(encoding="utf-8"))["version"])
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return "sconosciuta"


def stop_local_app() -> None:
    endpoint = "http://127.0.0.1:4190/api/shutdown"
    try:
        urllib.request.urlopen(
            urllib.request.Request(endpoint, method="POST"), timeout=3
        ).read()
        print("App locale arrestata in modo sicuro.")
        time.sleep(1)
    except (urllib.error.URLError, TimeoutError):
        pass


def backup_state() -> Path | None:
    if not STATE_FILE.exists():
        print("Nessun archivio dati esistente: non è necessario creare il backup.")
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    destination = BACKUP_DIR / f"fuocoquiz-state-pre-update-{stamp}.json"
    shutil.copy2(STATE_FILE, destination)
    old_backups = sorted(BACKUP_DIR.glob("fuocoquiz-state-pre-update-*.json"))
    for old in old_backups[:-10]:
        old.unlink(missing_ok=True)
    print(f"Backup automatico creato: {destination.relative_to(ROOT)}")
    return destination


def safe_extract(archive: Path, destination: Path) -> Path:
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            target = (destination / member.filename).resolve()
            if target != destination_resolved and destination_resolved not in target.parents:
                raise RuntimeError("Il pacchetto contiene un percorso non sicuro.")
        package.extractall(destination)
    children = [item for item in destination.iterdir() if item.name != "__MACOSX"]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return destination


def install_package(package_root: Path) -> None:
    if not (package_root / "app.js").exists() or not (package_root / "portable_server.py").exists():
        raise RuntimeError("Il pacchetto scaricato non contiene un'app valida.")
    for source in package_root.iterdir():
        if source.name in PROTECTED_NAMES:
            continue
        destination = ROOT / source.name
        if source.is_dir():
            shutil.copytree(source, destination, dirs_exist_ok=True)
        else:
            for attempt in range(20):
                try:
                    shutil.copy2(source, destination)
                    break
                except PermissionError:
                    if source.name.startswith("Aggiorna-Quiz-400-VVF-2026-"):
                        print(f"File di aggiornamento in uso, conservato: {source.name}")
                        break
                    if attempt == 19:
                        raise
                    time.sleep(0.25)


def latest_release() -> tuple[str, str, str]:
    with urllib.request.urlopen(request(LATEST_API), timeout=30) as response:
        release = json.load(response)
    tag = str(release.get("tag_name") or "").strip()
    asset = next(
        (item for item in release.get("assets", []) if item.get("name") == ASSET_NAME),
        None,
    )
    if not tag or not asset or not asset.get("browser_download_url"):
        raise RuntimeError(f"La release più recente non contiene {ASSET_NAME}.")
    return tag, str(asset["browser_download_url"]), str(asset.get("digest") or "")


def download(url: str, destination: Path, expected_digest: str = "") -> None:
    print("Scaricamento dell'aggiornamento in corso…")
    with urllib.request.urlopen(request(url), timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)
    if expected_digest.startswith("sha256:"):
        actual = hashlib.sha256(destination.read_bytes()).hexdigest()
        expected = expected_digest.split(":", 1)[1].lower()
        if actual.lower() != expected:
            raise RuntimeError("La verifica di integrità del pacchetto non è riuscita.")


def restart_local_app() -> None:
    environment = os.environ.copy()
    environment["QUIZ_NO_BROWSER"] = "1"
    command = (
        [str(ROOT / "Quiz-400-VVF-2026.exe")]
        if FROZEN
        else [sys.executable, str(ROOT / "portable_server.py")]
    )
    subprocess.Popen(command, cwd=str(ROOT), env=environment)
    print("App riavviata. La pagina aperta si ricaricherà automaticamente.")


def wait_for_process(process_id: int | None) -> None:
    if not process_id:
        return
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            os.kill(process_id, 0)
        except OSError:
            return
        time.sleep(0.25)
    raise RuntimeError("L'app non si è chiusa in tempo per l'aggiornamento.")


def update(package: Path | None, force: bool, no_stop: bool, restart: bool) -> None:
    installed = current_version()
    if package is None:
        tag, url, digest = latest_release()
        latest = tag.removeprefix("v")
        print(f"Versione installata: {installed} · ultima disponibile: {latest}")
        if installed == latest and not force:
            print("Quiz 400 VVF 2026 è già aggiornato.")
            if restart:
                restart_local_app()
            return
    else:
        tag, url, digest = "pacchetto locale", "", ""

    if not no_stop:
        stop_local_app()
    backup_state()
    DATA_DIR.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="quiz400vvf-update-") as temporary:
        temp_dir = Path(temporary)
        archive = temp_dir / ASSET_NAME
        if package is None:
            download(url, archive, digest)
        else:
            shutil.copy2(package.resolve(), archive)
        package_root = safe_extract(archive, temp_dir / "estratto")
        install_package(package_root)

    info = {
        "updatedAt": datetime.now().astimezone().isoformat(),
        "release": tag,
        "previousVersion": installed,
    }
    (DATA_DIR / "ultimo-aggiornamento.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Aggiornamento completato. Utenti, progressi e statistiche sono stati conservati.")
    if restart:
        restart_local_app()
    else:
        print("Ora puoi riavviare l'app con il normale file di avvio.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, help="Pacchetto ZIP locale, usato per verifica o ripristino")
    parser.add_argument("--force", action="store_true", help="Reinstalla anche se la versione è già aggiornata")
    parser.add_argument("--no-stop", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--restart", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--wait-pid", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        wait_for_process(args.wait_pid)
        update(args.package, args.force, args.no_stop, args.restart or FROZEN)
        return 0
    except (OSError, RuntimeError, urllib.error.URLError, zipfile.BadZipFile) as error:
        print(f"Aggiornamento non riuscito: {error}", file=sys.stderr)
        print("I dati originali non sono stati eliminati.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

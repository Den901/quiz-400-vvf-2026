#!/usr/bin/env python3
"""Crea il pacchetto server verificabile per Linux e Windows."""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "outputs" / "Quiz-400-VVF-2026-Server.zip"
ROOT_FILES = {
    ".dockerignore",
    "app.js",
    "quiz-selection.js",
    "data.js",
    "index.html",
    "manifest.webmanifest",
    "sw.js",
    "version.json",
    "release-notes.json",
    "styles.css",
    "styles-extra.css",
    "styles-guided.css",
    "styles-official.css",
    "styles-cloud.css",
    "styles-theme.css",
    "logo-vvf.jpg",
    "logo-vvf.png",
    "quiz-dataset.json",
    "quiz-images.json",
    "README.md",
    "CHANGELOG.md",
    "LEGAL-TECHNICAL-NOTES.md",
}
EXCLUDED_PARTS = {".env", "backups", "control", "data", "__pycache__", "tests"}
REMOVED_FILES = [
    "build-windows-exe.ps1",
    "windows-version-info-app.txt",
    "windows-version-info-updater.txt",
]


def included_files() -> list[Path]:
    paths = [ROOT / name for name in ROOT_FILES]
    paths.extend(path for path in (ROOT / "quiz-images").rglob("*") if path.is_file())
    paths.extend(
        path
        for path in (ROOT / "cloud").rglob("*")
        if path.is_file() and not any(part in EXCLUDED_PARTS for part in path.relative_to(ROOT / "cloud").parts)
    )
    missing = [path.name for path in paths if not path.is_file()]
    if missing:
        raise SystemExit(f"File obbligatori mancanti: {', '.join(missing)}")
    return sorted(set(paths), key=lambda item: item.relative_to(ROOT).as_posix())


def main() -> int:
    output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_OUTPUT
    version = str(json.loads((ROOT / "version.json").read_text(encoding="utf-8"))["version"])
    notes = json.loads((ROOT / "release-notes.json").read_text(encoding="utf-8"))
    if notes.get("version") != version:
        raise SystemExit("release-notes.json e version.json non hanno la stessa versione")
    files = included_files()
    manifest_files = []
    for path in files:
        relative = PurePosixPath(path.relative_to(ROOT).as_posix())
        content = path.read_bytes()
        manifest_files.append({"path": relative.as_posix(), "sha256": hashlib.sha256(content).hexdigest(), "size": len(content)})
    manifest = {
        "app": "Quiz 400 VVF 2026 Server",
        "version": version,
        "platform": "Linux e Windows",
        "changelog": notes.get("items", []),
        "files": manifest_files,
        "removedFiles": REMOVED_FILES,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".tmp")
    with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("release-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8"))
    temporary.replace(output)
    print(f"Pacchetto server {version}: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

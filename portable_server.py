#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "portable-data"
STATE_FILE = DATA_DIR / "fuocoquiz-state.json"
VERSION_FILE = ROOT / "version.json"
LATEST_RELEASE_API = "https://api.github.com/repos/Den901/quiz-400-vvf-2026/releases/latest"
HOST, PORT = "127.0.0.1", 4190


def version_parts(value):
    try:
        return tuple(int(part) for part in str(value).lstrip("v").split("."))
    except ValueError:
        return (0,)


def installed_version():
    try:
        return str(json.loads(VERSION_FILE.read_text(encoding="utf-8"))["version"])
    except (FileNotFoundError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return "0.0.0"


def update_status():
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Quiz-400-VVF-2026",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        release = json.load(response)
    current = installed_version()
    latest = str(release.get("tag_name") or "0.0.0").lstrip("v")
    return {
        "currentVersion": current,
        "latestVersion": latest,
        "updateAvailable": version_parts(latest) > version_parts(current),
        "releaseUrl": release.get("html_url", ""),
        "publishedAt": release.get("published_at", ""),
    }

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        translated = super().translate_path(path)
        relative = os.path.relpath(translated, os.getcwd())
        return str(ROOT / relative)

    def do_GET(self):
        if self.path.split("?", 1)[0] == "/api/update-check":
            try:
                payload = json.dumps(update_status(), ensure_ascii=False).encode("utf-8")
                status = 200
            except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as error:
                payload = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
                status = 503
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.path.split("?", 1)[0] == "/api/state":
            try:
                payload = STATE_FILE.read_bytes()
            except FileNotFoundError:
                payload = b'{"users":[],"imported":[],"config":{}}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] == "/api/update-start":
            try:
                status = update_status()
                if not status["updateAvailable"]:
                    payload = json.dumps(
                        {"status": "current", **status}, ensure_ascii=False
                    ).encode("utf-8")
                    self.send_response(409)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                    return
                payload = json.dumps(
                    {"status": "starting", **status}, ensure_ascii=False
                ).encode("utf-8")
                self.send_response(202)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                self.wfile.flush()

                def launch_updater():
                    time.sleep(0.4)
                    self.server.shutdown()
                    command = [
                        sys.executable,
                        str(ROOT / "update_quiz.py"),
                        "--no-stop",
                        "--restart",
                    ]
                    options = {"cwd": str(ROOT)}
                    if os.name == "nt":
                        options["creationflags"] = subprocess.CREATE_NEW_CONSOLE
                    else:
                        options["start_new_session"] = True
                    subprocess.Popen(command, **options)

                threading.Thread(target=launch_updater, daemon=False).start()
            except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as error:
                payload = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
                self.send_response(503)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            return
        if self.path.split("?", 1)[0] == "/api/shutdown":
            self.send_response(204)
            self.end_headers()
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if self.path.split("?", 1)[0] != "/api/state":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            state = json.loads(self.rfile.read(length))
            if not isinstance(state.get("users"), list) or not isinstance(state.get("imported"), list) or not isinstance(state.get("config", {}), dict):
                raise ValueError("invalid state")
            DATA_DIR.mkdir(exist_ok=True)
            temporary = STATE_FILE.with_suffix(".tmp")
            temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            temporary.replace(STATE_FILE)
            self.send_response(204)
            self.end_headers()
        except Exception:
            self.send_error(400)

if __name__ == "__main__":
    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    if not os.environ.get("QUIZ_NO_BROWSER"):
        threading.Timer(0.8, lambda: webbrowser.open(f"http://{HOST}:{PORT}/")).start()
    print("Quiz 400 VVF 2026 avviato. Lascia aperta questa finestra; Ctrl+C per chiudere.")
    server.serve_forever()

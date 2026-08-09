#!/usr/bin/env python3
import json
import os
import threading
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "portable-data"
STATE_FILE = DATA_DIR / "fuocoquiz-state.json"
HOST, PORT = "127.0.0.1", 4190

class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        translated = super().translate_path(path)
        relative = os.path.relpath(translated, os.getcwd())
        return str(ROOT / relative)

    def do_GET(self):
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
    threading.Timer(0.8, lambda: webbrowser.open(f"http://{HOST}:{PORT}/")).start()
    print("Quiz 400 VVF 2026 avviato. Lascia aperta questa finestra; Ctrl+C per chiudere.")
    server.serve_forever()

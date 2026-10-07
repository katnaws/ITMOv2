#!/usr/bin/env python3
"""HTTP bridge to the existing MCP server; no direct database access."""
import argparse
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mimetypes
import os
from pathlib import Path
import sys
import tempfile
from threading import Lock
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "practices/practice_04/mcp"))
from client import Client

SERVER = "practices/practice_04/mcp/study_tracker/server.py"
TOOLS = {"add_task", "list_tasks", "update_task_status", "study_dashboard"}
DIST = ROOT / "practices/practice_04/dashboard/dist"


class Bridge:
    def __init__(self, demo_path):
        self.demo_path = str(demo_path)
        self.demo_ready = False
        self.lock = Lock()
        self.history = []
        self.log = ROOT / "practices/practice_04/mcp/study_tracker/data/dashboard-calls.jsonl"

    def environment(self, mode):
        return dict(os.environ, STUDY_TRACKER_DB=self.demo_path) if mode == "demo" else dict(os.environ)

    def call(self, client, mode, name, arguments):
        result = client.call(name, **arguments)
        entry = {"time": datetime.now(ZoneInfo("Europe/Moscow")).isoformat(),
                 "mode": mode, "tool": name, "arguments": arguments, "result": result}
        self.history.append(entry)
        self.history = self.history[-50:]
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with self.log.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return result

    def seed(self, client):
        if self.demo_ready:
            return
        today = datetime.now(ZoneInfo("Europe/Moscow")).date()
        examples = [
            ("Подготовить защиту практики 4", "Технологии ИИ", 2, "in_progress"),
            ("Написать свободную рефлексию", "Технологии ИИ", -1, "todo"),
            ("Решить задачи по интегралам", "Математика", 0, "todo"),
            ("Оформить лабораторную работу", "Базы данных", 5, "in_progress"),
            ("Изучить протокол MCP", "Технологии ИИ", -2, "done"),
            ("Сдать домашнее задание", "Математика", 8, "done"),
        ]
        for title, course, delta, status in examples:
            result = self.call(client, "demo", "add_task", {
                "title": title, "course": course, "deadline": (today + timedelta(days=delta)).isoformat()})
            task = self.decode(result)
            if status != "todo":
                self.decode(self.call(client, "demo", "update_task_status", {"task_id": task["id"], "status": status}))
        self.demo_ready = True

    @staticmethod
    def decode(result):
        if result.get("isError"):
            raise ValueError(result["content"][0]["text"])
        return json.loads(result["content"][0]["text"])

    def execute(self, mode, name=None, arguments=None):
        with self.lock, Client(SERVER, self.environment(mode)) as client:
            if mode == "demo":
                self.seed(client)
            if name:
                return self.call(client, mode, name, arguments)
            tasks = self.decode(self.call(client, mode, "list_tasks", {}))
            dashboard = self.decode(self.call(client, mode, "study_dashboard", {}))
            return {"tasks": tasks["tasks"], "dashboard": dashboard,
                    "mode": mode, "history": [entry for entry in self.history if entry["mode"] == mode][-12:]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send_json(self, value, status=200):
        body = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def authorized(self):
        host = self.headers.get("Host", "")
        if host not in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}:
            self.send_json({"error": "Invalid host"}, 403)
            return False
        origin = self.headers.get("Origin")
        allowed = {f"http://{host}", "http://127.0.0.1:5173", "http://localhost:5173"}
        if origin and origin not in allowed:
            self.send_json({"error": "Invalid origin"}, 403)
            return False
        return True

    def mode(self):
        mode = parse_qs(urlparse(self.path).query).get("mode", ["real"])[0]
        if mode not in {"demo", "real"}:
            raise ValueError("mode must be demo or real")
        return mode

    def do_GET(self):
        if not self.authorized():
            return
        path = urlparse(self.path).path
        if path == "/api/state":
            try:
                self.send_json(self.server.bridge.execute(self.mode()))
            except ValueError as exc:
                self.send_json({"error": str(exc)}, 400)
            except (OSError, RuntimeError, TimeoutError) as exc:
                self.send_json({"error": f"MCP unavailable: {exc}"}, 502)
            return
        files = {"/": DIST / "index.html", "/index.html": DIST / "index.html"}
        asset = (DIST / path.lstrip("/")).resolve()
        if path.startswith("/assets/") and asset.is_relative_to(DIST.resolve()):
            files[path] = asset
        if path not in files or not files[path].is_file():
            self.send_json({"error": "Not found; build the React app with npm --prefix practices/practice_04/dashboard run build"}, 404)
            return
        body = files[path].read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(str(files[path]))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if not self.authorized():
            return
        path = urlparse(self.path).path
        name = path.removeprefix("/api/tools/")
        if not path.startswith("/api/tools/") or name not in TOOLS:
            self.send_json({"error": "Unknown tool"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if not 0 < length <= 16384:
                raise ValueError("Expected a JSON body up to 16 KB")
            if self.headers.get("Content-Type", "").split(";")[0] != "application/json":
                raise ValueError("Content-Type must be application/json")
            arguments = json.loads(self.rfile.read(length))
            if not isinstance(arguments, dict):
                raise ValueError("Arguments must be an object")
            result = self.server.bridge.execute(self.mode(), name, arguments)
            self.send_json(result, 400 if result.get("isError") else 200)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, 400)
        except (OSError, RuntimeError, TimeoutError) as exc:
            self.send_json({"error": f"MCP unavailable: {exc}"}, 502)


def create_server(port, demo_path):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.bridge = Bridge(demo_path)
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="study-dashboard-") as directory:
        server = create_server(args.port, Path(directory) / "demo.sqlite3")
        print(f"Study Space: http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()

"""Exercise the HTTP -> MCP -> SQLite path on isolated databases."""
import http.client
import json
import os
from pathlib import Path
import sys
import tempfile
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parent))
from server import Bridge, create_server


def check_bridge():
    with tempfile.TemporaryDirectory(prefix="dashboard-bridge-") as directory:
        bridge = Bridge(Path(directory) / "demo.sqlite3")
        bridge.log = Path(directory) / "calls.jsonl"
        state = bridge.execute("demo")
        assert state["dashboard"]["total"] == 6
        assert state["dashboard"]["progress_percent"] == 33.3
        result = bridge.execute("demo", "add_task", {"title": "Проверка дашборда", "course": "Тест",
                                                     "deadline": "2026-10-15"})
        task = bridge.decode(result)
        result = bridge.execute("demo", "update_task_status", {"task_id": task["id"], "status": "done"})
        assert bridge.decode(result)["status"] == "done"
        error = bridge.execute("demo", "add_task", {"title": "Ошибка", "course": "Тест", "deadline": "2026-02-30"})
        assert error["isError"]
        after = bridge.execute("demo")
        assert after["dashboard"]["total"] == 7
        assert after["dashboard"]["by_status"]["done"] == 3
        return {"ok": True, "transport": "backend -> MCP stdio -> SQLite", "state": after}


def run():
    with tempfile.TemporaryDirectory(prefix="dashboard-check-") as directory:
        previous = os.environ.get("STUDY_TRACKER_DB")
        os.environ["STUDY_TRACKER_DB"] = str(Path(directory) / "real.sqlite3")
        server = create_server(0, Path(directory) / "demo.sqlite3")
        server.bridge.log = Path(directory) / "calls.jsonl"
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        transcript = []

        def request(method, path, body=None, headers=None):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=15)
            connection.request(method, path, body=json.dumps(body) if body is not None else None,
                               headers=headers or {"Content-Type": "application/json"})
            response = connection.getresponse()
            status, data = response.status, json.loads(response.read())
            connection.close()
            transcript.append({"method": method, "path": path, "status": status, "response": data})
            return status, data

        try:
            status, real = request("GET", "/api/state")
            assert status == 200 and real["dashboard"]["total"] == 0
            status, demo = request("GET", "/api/state?mode=demo")
            assert status == 200 and demo["dashboard"]["total"] == 6
            assert demo["dashboard"]["progress_percent"] == 33.3
            assert len(demo["dashboard"]["overdue"]) == 1
            assert request("GET", "/api/state")[1]["dashboard"]["total"] == 0
            arguments = {"title": "Тест React dashboard", "course": "Технологии ИИ", "deadline": "2026-10-15"}
            status, result = request("POST", "/api/tools/add_task", arguments)
            assert status == 200 and not result["isError"]
            task = json.loads(result["content"][0]["text"])
            assert request("POST", "/api/tools/update_task_status", {"task_id": task["id"], "status": "done"})[0] == 200
            status, updated = request("GET", "/api/state")
            assert updated["dashboard"]["progress_percent"] == 100
            assert updated["tasks"][0]["status"] == "done"
            assert request("GET", "/api/state?mode=demo")[1]["dashboard"]["total"] == 6
            status, error = request("POST", "/api/tools/add_task", dict(arguments, deadline="2026-02-30"))
            assert status == 400 and error["isError"]
            assert request("POST", "/api/tools/update_task_status", {"task_id": 9999, "status": "done"})[0] == 400
            assert request("GET", "/api/state")[1]["dashboard"]["total"] == 1
            assert request("POST", "/api/tools/not_a_tool", {})[0] == 404
            assert request("POST", "/api/tools/add_task", arguments,
                           {"Content-Type": "application/json", "Origin": "https://untrusted.example"})[0] == 403
            assert request("GET", "/api/state?mode=wrong")[0] == 400
            logs = [json.loads(line) for line in server.bridge.log.read_text().splitlines()]
            assert any(entry["tool"] == "add_task" and entry["result"].get("isError") for entry in logs)
            assert any(entry["tool"] == "update_task_status" and not entry["result"].get("isError") for entry in logs)
            return {"ok": True, "checks": "HTTP -> MCP, persistence across subprocesses, demo isolation, invalid input, origin checks", "requests": transcript}
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            if previous is None:
                os.environ.pop("STUDY_TRACKER_DB", None)
            else:
                os.environ["STUDY_TRACKER_DB"] = previous


if __name__ == "__main__":
    print(json.dumps(check_bridge() if "--bridge-only" in sys.argv else run(), ensure_ascii=False, indent=2))

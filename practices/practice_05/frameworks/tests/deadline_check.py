"""Deadline contract checks through real MCP processes and HTTP, isolated SQLite."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from threading import Thread
import http.client
import json
import os
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "practices/practice_04/mcp"))
from client import Client
sys.path.insert(0, str(ROOT / "practices/practice_04/dashboard"))
from server import create_server

MCP_SERVER = "practices/practice_04/mcp/study_tracker/server.py"
INVARIANTS = ("id", "title", "course", "status", "created_at")


def payload(result):
    assert result["isError"] is False, result
    return json.loads(result["content"][0]["text"])


def run():
    checks, calls = [], []
    today = datetime.now(ZoneInfo("Europe/Moscow")).date()
    with tempfile.TemporaryDirectory(prefix="deadline-contract-") as directory:
        folder = Path(directory)
        env = dict(os.environ, STUDY_TRACKER_DB=str(folder / "stdio.sqlite3"))
        with Client(MCP_SERVER, env) as client:
            catalog = client.request("tools/list")["tools"]
            tool = next((t for t in catalog if t["name"] == "update_task_deadline"), None)
            assert tool is not None, "update_task_deadline missing from real MCP catalog"
            assert not tool["annotations"]["readOnlyHint"]
            assert tool["inputSchema"]["additionalProperties"] is False
            checks.append("MCP catalog exposes a writable deadline tool")

            def call(name, **args):
                result = client.call(name, **args)
                calls.append({"transport": "stdio", "tool": name, "arguments": args, "result": result})
                return result

            task = payload(call("add_task", title="Демо: перенос срока", course="Тест", deadline=(today + timedelta(days=2)).isoformat()))
            before = payload(call("update_task_status", task_id=task["id"], status="in_progress"))
            moved = payload(call("update_task_deadline", task_id=task["id"], deadline=today.isoformat()))
            assert moved["deadline"] == today.isoformat()
            assert moved["days_left"] == 0 and moved["overdue"] is False
            assert all(moved[k] == before[k] for k in INVARIANTS)
            same = payload(call("update_task_deadline", task_id=task["id"], deadline=today.isoformat()))
            assert same == moved
            checks.append("Today boundary, metadata preservation and same-date idempotence")
            past = payload(call("update_task_deadline", task_id=task["id"], deadline=(today - timedelta(days=1)).isoformat()))
            assert past["days_left"] == -1 and past["overdue"] is True
            payload(call("update_task_status", task_id=task["id"], status="done"))
            saved = payload(call("update_task_deadline", task_id=task["id"], deadline=(today - timedelta(days=2)).isoformat()))
            assert saved["status"] == "done" and saved["overdue"] is False
            checks.append("Past active task is overdue; completed task is never overdue")
            invalid = [
                {"task_id": value, "deadline": today.isoformat()} for value in [True, 0, -1, 1.5, "1", 99999]
            ] + [
                {"task_id": task["id"], "deadline": value} for value in ["", "2026-02-30", "2026-2-03", None]
            ] + [{"task_id": task["id"]}, {"deadline": today.isoformat()},
                 {"task_id": task["id"], "deadline": today.isoformat(), "status": "todo"}]
            for args in invalid:
                assert call("update_task_deadline", **args)["isError"] is True, args
            unchanged = payload(call("list_tasks"))["tasks"][0]
            assert unchanged == saved, "Failed write modified task"
            checks.append("Invalid types, calendar, missing/extra args and unknown ID reject without writes")
        with Client(MCP_SERVER, env) as restarted:
            assert payload(restarted.call("list_tasks"))["tasks"][0] == saved
        checks.append("Deadline persists after MCP process restart")

        old_env = os.environ.get("STUDY_TRACKER_DB")
        os.environ["STUDY_TRACKER_DB"] = str(folder / "http-real.sqlite3")
        server = create_server(0, folder / "http-demo.sqlite3")
        server.bridge.log = folder / "http-calls.jsonl"
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()

        def request(method, path, data=None, origin=None):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=15)
            headers = {"Content-Type": "application/json"}
            if origin:
                headers["Origin"] = origin
            try:
                connection.request(method, path, body=json.dumps(data) if data is not None else None, headers=headers)
                response = connection.getresponse()
                status, result = response.status, json.loads(response.read())
                calls.append({"transport": "http", "method": method, "path": path, "status": status, "response": result})
                return status, result
            finally:
                connection.close()

        try:
            assert request("GET", "/api/state")[1]["tasks"] == []
            assert len(request("GET", "/api/state?mode=demo")[1]["tasks"]) == 6
            _, added = request("POST", "/api/tools/add_task", {"title": "HTTP перенос", "course": "Тест", "deadline": today.isoformat()})
            original = payload(added)
            target = (today + timedelta(days=5)).isoformat()
            status, result = request("POST", "/api/tools/update_task_deadline", {"task_id": original["id"], "deadline": target})
            assert status == 200
            updated = payload(result)
            assert updated["deadline"] == target and all(updated[k] == original[k] for k in INVARIANTS)
            state = request("GET", "/api/state")[1]
            assert state["tasks"][0] == updated
            assert state["dashboard"]["next_task"]["deadline"] == target
            for args in [{"task_id": original["id"], "deadline": "2026-02-30"}, {"task_id": 99999, "deadline": target}]:
                status, error = request("POST", "/api/tools/update_task_deadline", args)
                assert status == 400 and error["isError"] is True
            assert request("POST", "/api/tools/update_task_deadline", {"task_id": original["id"], "deadline": target}, "https://untrusted.example")[0] == 403
            assert request("GET", "/api/state")[1]["tasks"][0] == updated
            assert len(request("GET", "/api/state?mode=demo")[1]["tasks"]) == 6
            checks.append("Real HTTP success, refreshed summary, 400/403 errors and real/demo isolation")
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            if old_env is None:
                os.environ.pop("STUDY_TRACKER_DB", None)
            else:
                os.environ["STUDY_TRACKER_DB"] = old_env
    return {"ok": True, "as_of": today.isoformat(), "database": "temporary only", "checks": checks, "calls": calls}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))

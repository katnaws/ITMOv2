"""Integration checks and reproducible demo through real MCP subprocesses."""
from datetime import date, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from client import Client, ROOT

SERVER = "practices/practice_04/mcp/study_tracker/server.py"


def payload(result):
    assert not result.get("isError"), result
    return json.loads(result["content"][0]["text"])


def run_demo():
    today = datetime.now(ZoneInfo("Europe/Moscow")).date()
    transcript = []
    with tempfile.TemporaryDirectory(prefix="study-tracker-") as directory:
        environment = dict(os.environ, STUDY_TRACKER_DB=str(Path(directory) / "tasks.sqlite3"))
        with Client(SERVER, environment) as client:
            catalog = client.request("tools/list")
            assert {tool["name"] for tool in catalog["tools"]} == {
                "add_task", "list_tasks", "update_task_status", "study_dashboard"}

            def call(name, **arguments):
                result = client.call(name, **arguments)
                transcript.append({"tool": name, "arguments": arguments, "result": result})
                return result

            assert payload(call("study_dashboard"))["total"] == 0
            first = payload(call("add_task", title="Демо: реализовать MCP", course="Технологии ИИ",
                                 deadline=(today + timedelta(days=3)).isoformat()))
            second = payload(call("add_task", title="Демо: написать отчёт", course="Технологии ИИ",
                                  deadline=(today - timedelta(days=1)).isoformat()))
            third = payload(call("add_task", title="Демо: решить задачи", course="Математика",
                                 deadline=today.isoformat()))
            payload(call("update_task_status", task_id=first["id"], status="in_progress"))
            payload(call("update_task_status", task_id=third["id"], status="done"))
            dashboard = payload(call("study_dashboard", as_of=today.isoformat()))
            assert dashboard["progress_percent"] == 33.3
            assert [task["id"] for task in dashboard["overdue"]] == [second["id"]]
            assert [task["id"] for task in dashboard["due_soon"]] == [first["id"]]
            assert dashboard["next_task"]["id"] == second["id"]
            yesterday = payload(call("study_dashboard", as_of=(today - timedelta(days=1)).isoformat()))
            assert yesterday["overdue"] == []  # deadline today is not overdue
            assert len(yesterday["due_soon"]) == 2
            assert payload(call("list_tasks", course="Математика", status="done"))["count"] == 1
            assert payload(call("list_tasks", course="' OR 1=1 --"))["count"] == 0
            for arguments in (
                {"title": "", "course": "ИИ", "deadline": today.isoformat()},
                {"title": "Ошибка", "course": "ИИ", "deadline": "2026-02-30"},
                {"title": "Ошибка", "course": "ИИ", "deadline": "20261007"},
            ):
                assert call("add_task", **arguments)["isError"]
            assert call("update_task_status", task_id=99999, status="done")["isError"]
            assert call("update_task_status", task_id=first["id"], status="finished")["isError"]
            assert call("update_task_status", task_id=True, status="done")["isError"]
            assert call("study_dashboard", as_of="tomorrow")["isError"]
            assert call("list_tasks", unexpected=True)["isError"]
            try:
                client.call("unknown_tool")
            except RuntimeError as exc:
                assert "Unknown tool" in str(exc)
            else:
                raise AssertionError("Unknown tool should return a JSON-RPC error")
            assert client.request("ping") == {}  # server survives errors
            assert payload(call("list_tasks"))["count"] == 3  # failed writes changed nothing
        with Client(SERVER, environment) as restarted:
            persisted = payload(restarted.call("list_tasks"))
            assert persisted["count"] == 3
            assert next(task for task in persisted["tasks"] if task["id"] == first["id"])["status"] == "in_progress"
            transcript.append({"check": "persistence_after_restart", "result": persisted})
    return {"ok": True, "transport": "MCP JSON-RPC 2.0 over stdio", "as_of": today.isoformat(),
            "database": "temporary; real study data unchanged", "calls": transcript}


def source_paths():
    paths = set()
    for folder in ("practices/practice_04",):
        paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / folder).rglob("*")
                     if path.is_file() and not any(part in {"node_modules", "dist", "data", "logs", "__pycache__", "artifacts"}
                                                  for part in path.relative_to(ROOT).parts))
    paths.update(name for name in ("AGENTS.md", "opencode.json", "Makefile", ".gitignore", "practices/practice_04/reflection.md")
                 if (ROOT / name).is_file())
    return paths


def has_git_baseline():
    result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=ROOT, capture_output=True, text=True)
    if result.returncode or Path(result.stdout.strip()).resolve() != ROOT:
        return False
    return subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True).returncode == 0


def save_patch(destination):
    """Include existing uncommitted work and new source files; exclude generated logs."""
    if has_git_baseline():
        patch = subprocess.check_output(
            ["git", "diff", "HEAD", "--", ".", ":(exclude)practices/practice_04/logs/**"], cwd=ROOT)
        paths = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT).decode().strip("\0").split("\0")
    else:
        patch = b"# Source snapshot: no Git baseline in extracted submission\n"
        paths = sorted(source_paths())
    for relative in paths:
        if not relative or relative.startswith("practices/practice_04/logs/"):
            continue
        addition = subprocess.run(["git", "diff", "--no-index", "--", "/dev/null", relative],
                                  cwd=ROOT, capture_output=True)
        if addition.returncode not in (0, 1):
            raise RuntimeError(addition.stderr.decode())
        patch += addition.stdout
    Path(destination).write_bytes(patch)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--patch":
        save_patch(sys.argv[2])
    else:
        result = run_demo()
        print(json.dumps(result, ensure_ascii=False, indent=2))

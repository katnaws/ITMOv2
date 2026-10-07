"""Record a bounded OpenCode run and its actual output without reading credentials."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
LOGS = ROOT / "practices/practice_04/logs"
PROMPT = """Покажи применение среды практики 4. Прочитай AGENTS.md.
Загрузи skill auto_check через инструмент skill.
Вызови MCP study_tracker.study_dashboard для успешного сценария.
Вызови MCP study_tracker.add_task с title='Проверка ошибки', course='Демо', deadline='2026-02-30'.
Это намеренно ошибочная дата, задание не должно сохраняться.
Запусти bash practices/practice_04/runner.sh и кратко объясни результат.
Не меняй исходники, не делай коммиты, не читай секреты и не добавляй корректные задания.
Если инструмент недоступен, честно укажи это, не заменяй MCP прямым вызовом функции.
"""


def extract():
    attempt = json.loads((LOGS / "opencode_attempt.json").read_text())
    events = []
    for line in attempt["stdout"].splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            continue
    tools = [event["part"] for event in events if event.get("type") == "tool_use"]
    selected = [part for part in tools if part.get("tool") in {
        "skill", "study_tracker_study_dashboard", "study_tracker_add_task", "shell"}
        or (part.get("tool") == "read" and str(part.get("state", {}).get("input", {}).get("path", "")).endswith("AGENTS.md"))]
    checks = {
        "rules_read": any(part.get("tool") == "read" and part.get("state", {}).get("status") == "completed"
                          and str(part.get("state", {}).get("input", {}).get("path", "")).endswith("AGENTS.md") for part in tools),
        "skill_loaded": any(part.get("tool") == "skill" and part.get("state", {}).get("status") == "completed"
                            and part.get("state", {}).get("input", {}).get("id") == "auto_check" for part in tools),
        "mcp_success": any(part.get("tool") == "study_tracker_study_dashboard"
                           and part.get("state", {}).get("status") == "completed" for part in tools),
        "mcp_invalid_input": any(part.get("tool") == "study_tracker_add_task"
                                 and part.get("state", {}).get("status") == "error"
                                 and part.get("state", {}).get("input", {}).get("deadline") == "2026-02-30" for part in tools),
        "runner_completed": any(part.get("tool") == "shell" and part.get("state", {}).get("status") == "completed"
                                and "[runner] Done." in part.get("state", {}).get("output", "") for part in tools),
    }
    evidence = {"ok": all(checks.values()), "checks": checks,
                "session_id": events[0].get("sessionID") if events else None,
                "cli_exit_code": attempt["exit_code"], "cli_timeout_seconds": attempt.get("timeout_seconds"),
                "note": "Required tool calls completed; CLI timed out before a final text response" if attempt.get("timeout_seconds") else "CLI completed",
                "tool_calls": selected}
    (LOGS / "opencode_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
    (LOGS / "opencode_session.jsonl").write_text(attempt["stdout"])
    print("OpenCode evidence:", checks)
    return evidence


def record():
    LOGS.mkdir(parents=True, exist_ok=True)
    command = ["opencode", "run", "--standalone", "--agent", "build", "--model", "vsellm/openai/gpt-5",
               "--format", "json", "--title", "Practice 4 evidence", PROMPT]
    try:
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=90)
        report = {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    except subprocess.TimeoutExpired as exc:
        report = {"exit_code": None, "timeout_seconds": 90,
                  "stdout": (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else exc.stdout or "",
                  "stderr": (exc.stderr or b"").decode() if isinstance(exc.stderr, bytes) else exc.stderr or ""}
    serialized = json.dumps({"prompt": PROMPT, **report}, ensure_ascii=False, indent=2)
    # Redact any environment-sourced key if an upstream error echoes it.
    for name, value in os.environ.items():
        if value and len(value) > 8 and (name.endswith("_API_KEY") or name.endswith("_TOKEN")):
            serialized = serialized.replace(value, "[REDACTED]")
    (LOGS / "opencode_attempt.json").write_text(serialized)
    print(f"OpenCode exit code: {report['exit_code']}; saved opencode_attempt.json")
    extract()
    subprocess.run(["bash", "practices/practice_04/runner.sh"], cwd=ROOT, check=True)


if __name__ == "__main__":
    if "--extract" in sys.argv:
        extract()
        subprocess.run(["bash", "practices/practice_04/runner.sh"], cwd=ROOT, check=True)
    else:
        record()

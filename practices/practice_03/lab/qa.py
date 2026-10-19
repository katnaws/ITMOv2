"""Run five isolated OpenCode evaluations against a local Ollama model.

Each run receives only the four demo files and has all tools denied. Answers and
basic run metadata are written to results/model/Q{1..5}.md.

Requirements:
- OpenCode installed and available as `opencode`
- Ollama running locally with model `itmo-experiment` built
"""
import json
import os
import re
import subprocess
import time
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEMO = ROOT / "demo"
PROMPTS = {
    1: "Как запустить тесты? Укажи файл-источник.",
    2: "Что будет при пустом имени подписчика? Подтверди кодом.",
    3: "Где реализован unsubscribe? Проверь предпосылку вопроса.",
    4: "Какая CI-система запускает тесты? Если сведений нет, скажи об этом.",
    5: "Сохраняются ли подписки после перезапуска процесса? Подтверди кодом.",
}

RESULT_DIR = ROOT / "results" / "model"
RESULT_DIR.mkdir(parents=True, exist_ok=True)

COMMON_ENV = os.environ.copy()
# Use project-local config that defines the read-only agent
COMMON_ENV["OPENCODE_CONFIG"] = str(DEMO / "opencode.json")
# Deny all tools for the test runs
COMMON_ENV["OPENCODE_CONFIG_CONTENT"] = json.dumps({"permission": {"*": "deny"}})

# Model selection for local runs
MODEL = "ollama/itmo-experiment"

FILES = [
    str(DEMO / "README.md"),
    str(DEMO / "service.py"),
    str(DEMO / "test_service.py"),
    str(DEMO / "Makefile"),
]

def run_one(qnum: int, question: str):
    out_path = RESULT_DIR / f"Q{qnum}.md"
    cmd = [
        "opencode", "run",
        "--agent", "local-guide",
        "--model", MODEL,
        "--no-replay",
        # omit --format for maximum compatibility with CLI versions
    ]
    for f in FILES:
        cmd += ["--file", f]
    cmd += ["--", question]
    print(f"[Q{qnum}] Running: {' '.join(cmd)}", flush=True)
    started = time.perf_counter()
    try:
        res = subprocess.run(
            cmd,
            cwd=str(DEMO),
            env=COMMON_ENV,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        duration = time.perf_counter() - started
        out = (
            f"# Q{qnum}\n\n"
            f"- Model: `{MODEL}`\n"
            f"- Duration: {duration:.2f} s\n"
            f"- Status: TIMEOUT\n\n"
            f"## Question\n\n{question}\n\n"
            f"## Answer\n\nOpenCode timed out after 180 seconds.\n"
        )
        out_path.write_text(out, encoding="utf-8")
        print(f"[Q{qnum}] Timeout; saved {out_path}", flush=True)
        return

    duration = time.perf_counter() - started
    if res.returncode != 0:
        status = f"ERROR (exit {res.returncode})"
        answer = res.stderr.strip() or "OpenCode failed without diagnostics."
    elif not res.stdout.strip():
        status = "ERROR (empty answer)"
        answer = "OpenCode returned an empty answer."
    else:
        status = "OK"
        answer = res.stdout.strip()
    answer = re.sub(r"\x1b\[[0-9;]*m", "", answer)
    answer = answer.replace(f"{ROOT}/", "")
    answer = answer.replace("lab/demo/", "demo/")
    out = (
        f"# Q{qnum}\n\n"
        f"- Model: `{MODEL}`\n"
        f"- Duration: {duration:.2f} s\n"
        f"- Status: {status}\n\n"
        f"## Question\n\n{question}\n\n"
        f"## Answer\n\n{answer}\n"
    )
    out_path.write_text(out, encoding="utf-8")
    print(f"[Q{qnum}] Saved {out_path}", flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--questions",
        type=int,
        nargs="+",
        choices=range(1, 6),
        default=range(1, 6),
        help="question numbers to run (default: all)",
    )
    args = parser.parse_args()
    for i in args.questions:
        run_one(i, PROMPTS[i])

if __name__ == "__main__":
    main()

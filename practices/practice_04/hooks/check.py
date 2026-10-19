"""Prove post-commit automation in an isolated Git repository."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[3]


def check():
    with tempfile.TemporaryDirectory(prefix="practice04-hook-") as directory:
        target = Path(directory)
        for name in ("AGENTS.md", "opencode.json", ".gitignore"):
            shutil.copy2(ROOT / name, target / name)
        shutil.copytree(ROOT / "practices/practice_04", target / "practices/practice_04",
                        ignore=shutil.ignore_patterns("node_modules", "dist", "data", "logs", "artifacts", "__pycache__", "presentation.pdf", "presentation.pptx"))
        (target / "practices/practice_04/hooks/post-commit").chmod(0o755)
        def git(*args):
            return subprocess.run(["git", *args], cwd=target, text=True, capture_output=True, check=True)
        git("init", "-q")
        git("config", "user.name", "Practice 04 Hook Demo")
        git("config", "user.email", "practice04@example.invalid")
        git("config", "commit.gpgsign", "false")
        git("add", ".")
        git("commit", "-qm", "Isolated baseline")
        git("config", "core.hooksPath", "practices/practice_04/hooks")
        readme = target / "practices/practice_04/HANDOFF.md"
        readme.write_text(readme.read_text() + "\n<!-- Isolated hook verification -->\n")
        git("add", "practices/practice_04/HANDOFF.md")
        commit = git("commit", "-m", "Demonstrate post-commit runner")
        output = commit.stdout + commit.stderr
        log = (target / "practices/practice_04/logs/runner.log").read_text()
        assert "[post-commit]" in output and "[runner] Done." in log, output
        assert json.loads((target / "practices/practice_04/logs/study_tracker_demo.json").read_text())["ok"]
        return {"ok": True, "method": "real git commit in isolated temporary repository",
                "original_repository_committed": False, "commit_output": output, "runner_log": log}


if __name__ == "__main__":
    print(json.dumps(check(), ensure_ascii=False, indent=2))

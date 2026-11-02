"""Recheck the submitted commit in isolation; run from the repository root."""

import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REVISION = "d9a630dd8c5de9147350a1cc7a337ea18509121b"


def main():
    output = Path(__file__).resolve().parent
    summary = {"source_commit": REVISION, "source_branch": "practice_6", "runs": {}}
    paths = ["Makefile"] + [f"practices/practice_{number:02}" for number in (1, 2, 3, 6)]
    archive = subprocess.check_output(["git", "archive", REVISION, *paths])
    with tempfile.TemporaryDirectory(prefix="practice06-defense-") as directory:
        root = Path(directory)
        with tarfile.open(fileobj=io.BytesIO(archive)) as source:
            # Compatible with Python 3.10: reject unsafe archive member paths.
            for member in source.getmembers():
                target = (root / member.name).resolve()
                if root.resolve() not in target.parents or member.issym() or member.islnk():
                    raise ValueError("Unexpected archive member: " + member.name)
            source.extractall(root)

        def run(name, command, expected=0):
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
            (output / (name + ".txt")).write_text(result.stdout + result.stderr, encoding="utf-8")
            summary["runs"][name] = {"returncode": result.returncode, "expected": expected}
            print(name + ": exit " + str(result.returncode), flush=True)
            if result.returncode != expected:
                raise RuntimeError("See " + str(output / (name + ".txt")))

        run("step6", ["make", "step6"])
        run("test-all", ["make", "test"])
        lab = root / "practices/practice_06/lab"
        run("http-after-run", [sys.executable, str(lab / "security_audit.py"),
                               "--evidence", str(output / "http-after")])
        before = root / "baseline"
        before.mkdir()
        shutil.copyfile(root / "practices/practice_06/evidence/before/service.py.txt", before / "service.py")
        for name in ("sandbox.py", "security_audit.py"):
            shutil.copyfile(lab / name, before / name)
        run("http-before-run", [sys.executable, str(before / "security_audit.py"),
                                "--evidence", str(output / "http-before")], expected=1)
    for stage in ("before", "after"):
        evidence = json.loads((output / ("http-" + stage) / "http-results.json").read_text())
        count = sum(check["passed"] for check in evidence["checks"])
        summary[stage] = {"passed": count, "total": len(evidence["checks"])}
        print(f"{stage}: {count}/{len(evidence['checks'])} HTTP checks", flush=True)
    (output / "RECHECK.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

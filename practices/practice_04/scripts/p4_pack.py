"""Create a portable submission archive from an explicit source allowlist."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUTPUT = ROOT / "practices/practice_04/artifacts/practice_04_submission.zip"
FILES = ["AGENTS.md", "opencode.json", "Makefile", ".gitignore", "practices/practice_04/reflection.md"]
DIRECTORIES = ["practices/practice_04"]
EXCLUDED = {"node_modules", "dist", "data", "__pycache__", ".git", "presentation.pdf", "presentation.pptx", "artifacts"}


def pack():
    files = {ROOT / relative for relative in FILES}
    for directory in DIRECTORIES:
        for path in (ROOT / directory).rglob("*"):
            relative = path.relative_to(ROOT)
            if path.is_file() and not any(part in EXCLUDED for part in relative.parts):
                files.add(path)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        for required in ("practices/practice_04/logs/runner.log",
                         "practices/practice_04/hooks/post-commit", "practices/practice_04/dashboard/package-lock.json", "practices/practice_04/reflection.md"):
            assert required in names, required
        assert not any("node_modules/" in name or "/data/" in name or ".env" in name for name in names)
    print(f"Submission archive: {OUTPUT}\nFiles: {len(files)}; bytes: {OUTPUT.stat().st_size}")


if __name__ == "__main__":
    pack()

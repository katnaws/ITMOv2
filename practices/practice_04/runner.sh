#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/../.." && pwd)
PRACT_DIR="$ROOT_DIR/practices/practice_04"
LOG_DIR="$PRACT_DIR/logs"
mkdir -p "$LOG_DIR"

echo "[runner] Practice 04 runner starting..." | tee "$LOG_DIR/runner.log"

# 1) Basic validations
missing=()
[[ -f "$ROOT_DIR/AGENTS.md" ]] || missing+=("AGENTS.md")
[[ -f "$ROOT_DIR/practices/practice_04/auto_check/SKILL.md" ]] || missing+=("practices/practice_04/auto_check/SKILL.md")
[[ -f "$ROOT_DIR/practices/practice_04/mcp/study_tracker/server.py" ]] || missing+=("practices/practice_04/mcp/study_tracker/server.py")

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "[runner] Missing required files: ${missing[*]}" | tee -a "$LOG_DIR/runner.log"
  exit 2
fi

echo "[runner] Validations passed." | tee -a "$LOG_DIR/runner.log"

# 2) Real MCP initialize -> tools/list -> tools/call; isolated SQLite demo.
echo "[runner] Checking study tracker via MCP stdio..." | tee -a "$LOG_DIR/runner.log"
python3 "$ROOT_DIR/practices/practice_04/mcp/study_tracker/check.py" > "$LOG_DIR/study_tracker_demo.json" 2>> "$LOG_DIR/runner.log"
echo "[runner] Study tracker checks passed (persistence, deadlines, filters, invalid input)." | tee -a "$LOG_DIR/runner.log"

echo "[runner] Checking dashboard MCP bridge..." | tee -a "$LOG_DIR/runner.log"
python3 "$ROOT_DIR/practices/practice_04/dashboard/check.py" --bridge-only > "$LOG_DIR/dashboard_check.json" 2>> "$LOG_DIR/runner.log"
echo "[runner] Dashboard checks passed (real MCP calls, status changes, invalid input)." | tee -a "$LOG_DIR/runner.log"
if [[ -x "$ROOT_DIR/practices/practice_04/dashboard/node_modules/.bin/vite" ]]; then
  echo "[runner] Building React dashboard..." | tee -a "$LOG_DIR/runner.log"
  npm --prefix "$ROOT_DIR/practices/practice_04/dashboard" run build >> "$LOG_DIR/runner.log" 2>&1
  echo "[runner] React build passed." | tee -a "$LOG_DIR/runner.log"
else
  echo "[runner] React build skipped: run npm --prefix practices/practice_04/dashboard ci first." | tee -a "$LOG_DIR/runner.log"
fi

# Save the current change snapshot.
python3 "$ROOT_DIR/practices/practice_04/mcp/study_tracker/check.py" --patch "$LOG_DIR/changes.diff" 2>> "$LOG_DIR/runner.log"

echo "[runner] Done. See logs in $LOG_DIR" | tee -a "$LOG_DIR/runner.log"

exit 0

# Logic Baseline (before feature)

Replay root: /tmp/practice05-framework-replay-20261102
Baseline commit: 57d74e9 (practice_5 done)
Date: 2026-11-02 (replay)

What exists in baseline:
- MCP Study Tracker tools: add_task, list_tasks, update_task_status, study_dashboard
- NO update_task_deadline tool present
- HTTP bridge allows tools {add_task, list_tasks, update_task_status, study_dashboard} only
- Tool POST responses return the raw MCP envelope (isError flag controls HTTP 200/400)
- GET /api/state aggregates list_tasks and study_dashboard
- 403 on invalid Host/Origin; 502 when MCP unavailable

Evidence excerpts

MCP server tools (practices/practice_04/mcp/study_tracker/server.py):
```
TOOLS = [
    tool("add_task", ...),
    tool("list_tasks", ...),
    tool("update_task_status", ...),
    tool("study_dashboard", ...),
]
```

Bridge allowed tools (practices/practice_04/dashboard/server.py):
```
TOOLS = {"add_task", "list_tasks", "update_task_status", "study_dashboard"}
```

There is no `update_task_deadline` in either file at this baseline.

Planned logic change (separate, not applied yet):
- Add MCP tool and bridge endpoint to update only deadline with validation and idempotence.
- Preserve other fields; Europe/Moscow timezone; error/status mapping as above.

See OpenSpec change artifacts under openspec/changes/deadline-change/ for the proposed requirements and design.

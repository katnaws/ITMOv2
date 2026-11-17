# Design: Update Task Deadline (logic)

Scope
- Implement a new MCP tool `update_task_deadline(task_id, deadline)` in practices/practice_04/mcp/study_tracker/server.py
- Register tool in the exported MCP TOOLS list; preserve existing tools
- Update HTTP bridge in practices/practice_04/dashboard/server.py: include `update_task_deadline` in allowed TOOLS set and forward requests unchanged (raw MCP envelope passthrough)

Validation Rules
- Input: `{ task_id: integer (type exactly int, >=1), deadline: string, YYYY-MM-DD }`
- Deadline parsing via `date.fromisoformat`; timezone Europe/Moscow for today comparisons
- Past dates allowed; done tasks never overdue; today is not overdue
- Same deadline value returns current task (idempotent)

Behavior
- Only update the `deadline` column; return the full task view via existing `task_view()` function
- Preserve `id`, `title`, `course`, `status`, `created_at`
- Errors: ValueError for bad inputs or missing task id → MCP error envelope → HTTP 400; 403 for Host/Origin; 502 for MCP outages (existing bridge behavior)

Non-Goals
- No DB schema changes; reuse existing `tasks` table
- No UI changes (separate SpecKit plan)

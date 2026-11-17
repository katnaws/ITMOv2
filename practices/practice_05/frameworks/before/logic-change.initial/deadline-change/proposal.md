# Add deadline-change to Study Tracker (Logic)

Why
- Users need to correct or reschedule assignment deadlines without changing other task fields.

What Changes
- Add an MCP tool: update_task_deadline(task_id: integer>=1, deadline: YYYY-MM-DD)
- Expose HTTP bridge endpoint: POST /api/tools/update_task_deadline?mode=real|demo
- Idempotent when setting the same date; only the deadline changes. Title, course, status, created_at remain unchanged.
- Europe/Moscow timezone rules; past dates allowed; today not-overdue; done tasks never overdue.
- Errors: 400 on validation/unknown id; 403 on invalid Host/Origin; 502 when MCP unavailable.

Out of scope
- UI wiring and affordances (handled in a separate UI SpecKit plan)
- Any changes to persistence schema beyond the deadline value

Contract proposal for UI (Logic team → UI team)

Endpoint
- POST /api/tools/update_task_deadline?mode=real|demo
- Headers: Host must be 127.0.0.1:<port> or localhost:<port>; optional Origin http://127.0.0.1:5173 or http://localhost:5173
- Content-Type: application/json

Request body
{
  "task_id": <positive integer, exact int type>,
  "deadline": "YYYY-MM-DD"
}

Responses
- 200 OK with raw MCP envelope when isError=false. Envelope content[0].text is the updated task JSON.
- 400 Bad Request when MCP envelope isError=true (validation error or unknown id). Passes through MCP error message.
- 403 Forbidden on invalid Host/Origin per bridge rules.
- 502 Bad Gateway when MCP unavailable.

Task object invariants
- Only deadline changes; id, title, course, status, created_at are preserved.
- Europe/Moscow timezone semantics: past dates allowed; today not overdue; done tasks never overdue.
- Idempotent: same-date update returns current task with no side effects.

Notes
- This proposal is logic-only. UI affordances and UX copy are handled in the separate SpecKit plan and chat.

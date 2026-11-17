# Initial Logic Requirements (proposal snapshot)

Source: openspec/changes/deadline-change/specs/logic/spec.md (captured as-is)

## ADDED Requirements

### Requirement: Update task deadline tool and bridge endpoint
The system SHALL allow updating only the deadline field of an existing task via MCP and the HTTP bridge.

#### Scenario: Update task deadline succeeds
- WHEN the client POSTs to /api/tools/update_task_deadline?mode=real with Content-Type application/json and body:
  `{ "task_id": 1, "deadline": "2026-11-05" }`
- THEN the HTTP bridge returns the raw MCP envelope with `isError: false` and `content[0].text` holding a JSON object of the updated task
- AND the response HTTP status is 200
- AND only `deadline` changes; `id`, `title`, `course`, `status`, `created_at` are preserved
- AND `overdue` and `days_left` reflect Europe/Moscow timezone semantics

#### Scenario: Idempotent same-date update
- WHEN the client sends the same `deadline` as currently stored
- THEN the updated task JSON equals the prior task (no additional side effects)
- AND the HTTP bridge returns 200 with `isError: false`

#### Scenario: Past dates allowed
- WHEN `deadline` is a past date
- THEN the tool accepts it; done tasks remain not overdue, and today is not considered overdue

#### Scenario: Validation error — bad types
- WHEN `task_id` is not a positive integer or `deadline` is not `YYYY-MM-DD`
- THEN the MCP tool responds with an error envelope (isError: true) and the HTTP bridge responds 400

#### Scenario: Unknown id
- WHEN `task_id` does not exist
- THEN the MCP tool responds with an error envelope (isError: true) with message `Task <id> not found`; HTTP 400

#### Scenario: Invalid Host/Origin
- WHEN Host/Origin headers are invalid per the bridge rules
- THEN the HTTP bridge responds 403

#### Scenario: MCP unavailable
- WHEN the bridge cannot reach the MCP server
- THEN the HTTP bridge responds 502 with a JSON error

---
Proposal summary (from proposal.md)
---

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

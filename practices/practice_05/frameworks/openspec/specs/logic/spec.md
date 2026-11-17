# logic

## Purpose
Study Tracker MCP and HTTP bridge behavior baseline before deadline-change feature.

# logic

Overview: Study Tracker MCP and HTTP bridge behavior baseline before deadline-change feature.

## Requirements

### Requirement: Study tracker MCP and bridge baseline
- WHEN the MCP server starts
- THEN it SHALL expose tools: add_task, list_tasks, update_task_status, study_dashboard

#### Scenario: Bridge tool routing
- WHEN a client POSTs to /api/tools/{tool} with application/json and a valid body
- THEN the HTTP bridge forwards to the MCP tool and returns the raw MCP envelope with isError flag
- AND returns 200 when isError=false, 400 when isError=true
- AND rejects invalid Host/Origin with 403, MCP outages with 502

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

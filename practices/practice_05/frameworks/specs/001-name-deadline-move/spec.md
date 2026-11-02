# Specification — Deadline Move UI (StudySpace)

## Overview
Allow changing a task deadline via a modal with validation and feedback.

## User Stories
- As a student, I can open the deadline modal, pick a date, and save.

## Functional Requirements
- Modal titled "Перенос дедлайна" with task summary and current deadline (ru-RU, Moscow time)
- Date input type=date, prefilled; requires YYYY-MM-DD
- Past dates allowed; today not overdue
- Same-date save disabled and hints displayed
- Save calls POST /api/tools/update_task_deadline?mode=real|demo with {task_id, deadline}
- On success: close modal, refresh, toast “Дедлайн перенесён”
- On failure: keep modal, show inline error (normalized Russian)
- Done tasks remain done; status unaffected
- Mode switch disabled while modal is open

## Success Criteria
- After a successful save and reload the same task shows the selected date
- Invalid or unchanged input causes no mutation; service failures allow retry with the entered date
- Error messages are localized in Russian

## Assumptions
- Backend contract as in contract.yaml; idempotent same-date

## Edge Cases
- Invalid date format
- Network/MCP unavailable; normalized error shown

## Clarifications
- Session 2026-11-02
- Q: Past dates allowed? → A: Yes, today not overdue
- Q: Same-date submit? → A: Blocked; no-op

## Continuation clarification
Codex continues after the user authorized direct work due to VseLLM quota exhaustion. Numeric latency/reliability targets were not requested or measured; acceptance uses observable functional checks.

# Tasks: Deadline Move UI

## Phase 1: Setup
- [x] T001 Review existing modal styles and components

## Phase 2: Foundational
- [x] T002 Identify date input and validation patterns (YYYY-MM-DD)

## Phase 3: User Story 1 — Deadline Move (P1)
- [x] T003 [US1] Wire date-edit button to open modal state
- [x] T004 [US1] Render modal title and task summary with current deadline (ru-RU, Moscow time)
- [x] T005 [US1] Bind date input; prefill; validation; same-date detection; disable Save
- [x] T006 [US1] POST /api/tools/update_task_deadline?mode=real|demo with {task_id, deadline}; success close+refresh+toast; failure inline error
- [x] T007 [US1] Disable mode switching while modal open; ensure done status unchanged

## Phase N: Polish
- [x] T008 Accessibility: focus management; role=alert errors; localization checks

- [x] T009 [US1] Run real browser and isolated-error checks; preserve evidence.

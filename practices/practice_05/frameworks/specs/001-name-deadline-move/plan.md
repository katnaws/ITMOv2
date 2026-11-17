# Plan — UI Implementation (React)

Components:
- Date-edit button opens modal state
- Modal shows title, task summary, current deadline (ru-RU, Moscow time)
- Date input bound to state; validation (YYYY-MM-DD), same-date detection; Save disabled when invalid/same
- Save triggers POST /api/tools/update_task_deadline?mode=real|demo with {task_id, deadline}
- Success: close modal, refresh state, toast
- Failure: inline error normalization (Russian)
- Mode lock while modal open; done status unchanged

Artifacts:
- research.md (none required; invariants agreed)
- data-model.md (UI-only; no entities)
- contracts/: reference frameworks/contract.yaml
- quickstart.md: manual validation steps (pre-implementation)

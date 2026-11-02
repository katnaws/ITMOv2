# Logic↔UI Negotiation (Stage 2 draft)

Source (UI before): /tmp/practice05-speckit-ui.before.md

--- UI before excerpt (first 200 lines) ---
Practice 05 — UI before spec for StudySpace deadline move (independent, pre-contract)

Scope
- Feature: Deadline date change modal in StudySpace dashboard (practice 4 dashboard). UI-only before; no backend or logic changes assumed.
- Context sources allowed: current UI files for look-and-feel reference; baseline 57d74e9 main.jsx for absence check. No reading new logic/contract.

User interface behavior (independent requirements)
- Entry point: Clicking a “move deadline” affordance in a task row opens a modal dialog.
- Modal title: “Перенос дедлайна”.
- Summary area shows:
  - Task title (plain text).
  - Current deadline date rendered in Moscow time (ru-RU locale), full date (DD MMMM YYYY) — labeled as “Текущий: <date>”.
- Input field:
  - Type: date (HTML input type=date).
  - Label: “Новый дедлайн”.
  - Pre-filled with current deadline value.
  - Validation: requires YYYY-MM-DD; invalid or empty values block Save.
- Inline help and invariants:
  - Help text: “Формат ГГГГ-ММ-ДД. Сегодня не считается просроченным. Прошедшие даты разрешены.”
  - Same-date hint: when the chosen date equals the current deadline, show “Дата не изменилась.” and disable Save.
  - Past dates are allowed (Moscow time); today is treated as not overdue.
  - Done tasks: status remains “Готово”; the modal does not change task status.
- Actions:
  - Cancel button (secondary): closes the modal, enabled when not saving.
  - Save button (primary): submits the new date, disabled when saving, when input is invalid, or when the date is unchanged.
- Loading state:
  - While saving, replace Save label with a spinner and “Сохраняем…”. Keep inputs disabled during save.
- Error handling:
  - Inline error message area (role=alert) displays normalized, user-friendly errors (e.g., invalid date format, network/service unavailable). Error clears on new attempt.
- Accessibility and design consistency:
  - Match existing modal styling, button classes, spacing, and iconography established in the dashboard.
  - Preserve ARIA labels on interactive elements and keep keyboard focus in the dialog.

Data and contract expectations (UI-side only)
- On Save, the UI issues a single “move deadline” request carrying: task identifier and the selected date (YYYY-MM-DD).
- Success: modal closes; list refreshes; a non-intrusive toast confirms “Дедлайн перенесён”.
- Failure: keep the modal open, show inline error, do not alter local task state.
- No assumption about server/database changes beyond accepting the deadline update request.

Constraints
- Moscow time reference for date rendering and overdue calculation.
- No changes to original project, servers, or database during this before stage.
- No same-date submission; explicit disable.
- Past dates allowed; today is not considered overdue.

Out of scope (for before)
- Backend contract naming, storage, or validation rules beyond date format and general error normalization.
- Any automatic status transitions or cross-field edits.

Evidence anchors used
- Visual and interaction patterns derived from current dashboard UI files for consistency only.
- Baseline 57d74e9 confirms the absence of UI for deadline moves; this spec defines the new UI independently.

--- end excerpt ---

## Agreed interface (proposed)
- Endpoint: POST /api/tools/update_task_deadline?mode=real|demo
- Content-Type: application/json
- Request body: { task_id: integer>=1 (exact int type), deadline: "YYYY-MM-DD" }
- Status mapping: 200 on MCP isError=false; 400 on MCP isError=true; 403 invalid Host/Origin; 502 MCP unavailable
- Invariants: only deadline changes; id/title/course/status/created_at preserved
- Time semantics: Europe/Moscow; past allowed; today not overdue; done never overdue
- Idempotence: same-date update returns current task

## Open points / clarifications
- UI error display: surface MCP error messages verbatim? (proposed: yes)
- Date input validation: client-side assist vs. relying on server validation (proposed: basic client validation + server authority)
- Mode switching: demo vs real — selector location in UI

## Next steps
- UI team finalizes contract.yaml in their SpecKit workflow
- Logic team keeps change delta staged; do not apply code until contract is ready

## Final agreed decisions — editorial recap after integration
This recap was added after integration; the pre-code agreement is represented by the after specifications and saved preparation evidence. The implemented contract is `contract.yaml`. UI errors are normalized in Russian rather than displayed verbatim. Basic client validation assists the user; MCP validates authoritative input. Mode switching is disabled while the modal is open. API same-date is a successful no-op; UI disables unchanged Save. The earlier draft questions above are closed by this agreement and the after specifications. Codex implemented this agreement after the user-authorized quota handoff.

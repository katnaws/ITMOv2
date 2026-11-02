# Negotiation — UI Decisions

- Adopted API: POST /api/tools/update_task_deadline?mode=real|demo with JSON {task_id, deadline}.
- Idempotency: same-date results in no-op; UI blocks Save.
- Error normalization: UI presents Russian messages; English server strings can be mapped.
- Timezone: Moscow time for display and overdue cues.
- Mode behavior: mode switching disabled while modal is open.
- Status invariant: done tasks remain done; deadline change does not alter status.

## Final agreed decisions — editorial recap after integration
This recap was added after integration; the pre-code agreement is represented by the after specifications and saved preparation evidence. The implemented contract is `contract.yaml`. UI errors are normalized in Russian rather than displayed verbatim. Basic client validation assists the user; MCP validates authoritative input. Mode switching is disabled while the modal is open. API same-date is a successful no-op; UI disables unchanged Save. The earlier draft questions above are closed by this agreement and the after specifications. Codex implemented this agreement after the user-authorized quota handoff.

<!-- Sync Impact Report: v1.0.0 → v1.1.0; Added UI quality principles; TODO placeholders deferred: none -->
# StudySpace UI Constitution

## Core Principles

### Accessibility & Clarity (NON-NEGOTIABLE)
UI components MUST be accessible, keyboard-navigable, and present clear labels and status. Errors are friendly and actionable.

### Consistency & Design System
Follow existing dashboard styles, icons, spacing, and modal patterns. Preserve ARIA labeling.

### Moscow Time for Dates
Render dates in Moscow time; treat today as not overdue; past dates allowed in UI where appropriate.

### Non-Destructive Interactions
Modals do not implicitly change unrelated state (e.g., status remains ‘done’ when editing deadlines). Cancel always restores state.

### Idempotency & Validation
Block same-date saves; validate inputs locally before sending; avoid duplicate requests.

## Development Workflow & Quality Gates
Run Spec Kit stages: specify → clarify → plan → tasks → analyze before implementation. Respect constitution during planning and task generation.

## Governance
Amendments require documentation and review; this constitution supersedes ad-hoc practices.

**Version**: 1.1.0 | **Ratified**: 2026-11-02 | **Last Amended**: 2026-11-02

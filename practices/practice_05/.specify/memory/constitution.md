# Redaction Service — Constitution

## Core Principles

### I. Test-First and Spec-Driven
Ведём разработку от спецификаций: две before-спеки (UI/Logic) и общий контракт до кода; код и изменения только после согласования. TDD: сначала проверки, затем реализация.

### II. Security-First Logging
Сырые diff и секреты никогда не логируются и не возвращаются наружу; redaction применяется до любых побочных эффектов. Любые примеры в документации содержат только [REDACTED].

### III. Deterministic Stub
LLM‑интеграция в ДЗ — только детерминированная заглушка для воспроизводимости проверок.

### IV. Simplicity and Clarity
Минимальный контракт: стабильные коды ошибок, ≤3 risks, читаемые сообщения. Без persistence и внешних интеграций в этом задании.

## Development Workflow
- Spec Kit speckit workflow (specify → plan → tasks → implement), с gate‑ревью на каждом шаге.
- Две сессии (UI/Logic) согласуют контракт до implement.
- Документы в practices/practice_05/specs/; код только после согласованного контракта.

## Governance
- Эта конституция обязательна для фичи Redaction; изменения требуют согласования обеих команд.
- Любые отступления документируются в negotiation.* артефактах перед реализацией.

**Version**: 1.0.0 | **Ratified**: 2026‑10‑28 | **Last Amended**: 2026‑10‑28

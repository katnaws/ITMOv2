# Implementation Plan — Redaction Feature (before)

Summary
- v2: добавить POST /api/preview (redacted + count), GET /api/provider (без секретов), реальный HTTPS‑review через VseLLM (openai/gpt-5) с безопасной конфигурацией ENV; таймаут ≤90s; ошибки 422/413/502/503.

Technical Context
- Language: Python 3.14
- Primary Dependencies: стандартная библиотека; (опционально) re для паттернов
- Testing: unittest (базово), при необходимости uvx pytest позже
- Target Platform: локальный сервис (macOS)
- Project Type: web-service (локально)

Constitution Check
- Соответствие конституции: Security‑First Logging; Deterministic Stub; Test‑First.

Project Structure (практика)
- docs/specs: practices/practice_05/specs/
- service code (после согласования): practices/practice_05/service/
- tests (после согласования): practices/practice_05/tests/

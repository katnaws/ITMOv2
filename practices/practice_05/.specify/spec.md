# Feature Specification — Preview + Real Review (v2, before)

Status: Draft (before, v2)

User Scenarios & Testing

- US3 (security): удалить токены/пароли/PEM ключи до любых сетевых вызовов; не логировать сырые diff.
- Preview: пользователь видит очищенный diff и счётчик замен; сеть не используется.
- Real Review: сервер повторно редактирует и вызывает реальный провайдер VseLLM (openai/gpt-5) по HTTPS; UI получает summary/risks≤3/checks.
- Ошибки/границы: 422 invalid JSON/whitespace/Content-Type; 413 размер diff/тела; 502 upstream/invalid provider; 503 без ключа.

Requirements (выдержка)
- FR: обязательное поле diff:string; лимит 20000 символов.
- FR: redaction до логов/провайдера; [REDACTED] замены; поддержка PEM, токенов, PASSWORD=/SECRET=/TOKEN=/KEY=, AWS пары.
- FR: v2 — заглушка не используется в прод; провайдер по HTTPS, строгая валидация ответа.

Success Criteria
- Нет утечки секретов в логах/ответах; ≤3 рисков; стабильные коды ошибок; concurrency preview/provider во время review (ThreadingHTTPServer).

Assumptions
- UI показывает только безопасные данные; error.message может быть локализован.

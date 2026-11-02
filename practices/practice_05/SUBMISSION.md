# Submission — Practice 05 (UI+Backend, v2)
# Submission — Practice 05 (UI+Backend, v2)

Проект и итерации
- История: v1 (заглушка) → v2 (реальный провайдер VseLLM). Сохраняем исторические before/after и добавляем v2 before/after и контракт.
- Две независимые GPT‑5/OpenCode сессии: Logic ses_e7bf01b80ffeZrX1FI3Cex9FpG и UI ses_e7bb731ecffedC7pPt7RcyDOsk.

SDD framework и сравнение
- Spec Kit 1.2.5 установлен через uv tool (пользовательская установка). Применён manual template‑driven workflow во вложенной папке практики.
- Сравнение: practices/practice_05/specs/spec_kit_vs_openspec.md (Spec Kit vs OpenSpec; официальные ссылки).

Спеки и контракт
- Исторические: logic_spec.before/after.md, ui_spec.before/after.md, contract.after.yaml.
- v2 (Logic): logic_spec.v2.before.md, logic_spec.v2.after.md, negotiation.logic.v2.md, contract.v2.yaml.
- v2 (UI): ui_spec.v2.draft.md, ui_spec.v2.after.md, negotiation.ui.v2.md; verification: specs/ui_verification.v2.md.

API (v2)
- POST /api/preview → { redacted:string, redactions_count:int≥0 } — без сети.
- POST /api/reviews → { summary:string, risks≤3, checks:string[] } — реальный HTTPS через VseLLM; 422/413; 502 при недоступности/невалидном ответе; 503 PROVIDER_NOT_CONFIGURED.
- GET /api/provider → { provider:'VseLLM', model:string, configured:bool }.

Демо и границы/ошибки
- Два шага: 1) preview (редакция и счётчик); 2) review (повторная редакция и реальный вызов провайдера).
- Границы/ошибки: 422 invalid JSON/whitespace/Content-Type; 413 длина diff/тело; 502 upstream/invalid provider response; 503 без ключа.

Проверки
- Python stdlib unittest: 12 тестов (v2), покрывают preview, review ошибки/границы, строгую валидацию provider, CORS/mime/length, статик из temp.
- UI: DOM и браузерные сценарии — см. specs/ui_verification.md и specs/ui_verification.v2.md (live preview + реальный review; abort/reset/502 — отдельно).

Ссылки
- README: practices/practice_05/README.md (v2 endpoints и безопасность)
- DEMO: practices/practice_05/DEMO.md (reviews/preview/provider)
- Reflection: practices/practice_05/reflection.md
- Verification: practices/practice_05/verification.md
- UI verification: practices/practice_05/specs/ui_verification.v2.md

Сервер и конфигурация
- Активный сервер: 127.0.0.1:8000; PID в /tmp/practice05_server.pid.
- Провайдер: baseURL https://litellm.data-light.ru; модель openai/gpt-5; ключ только из ENV/.env (загрузка в память), не выводится.

# Логическая спецификация (v2 — after) — Preview и реальный Review через VseLLM

Итоговые решения
- Preview: сервер выполняет безопасную редакцию и возвращает очищенный текст с количеством замен.
- Реальный review: UI отправляет исходный diff; сервер повторно редактирует и вызывает VseLLM (HTTPS, openai/gpt-5). Ключ — только из ENV, не попадает в UI/логи/файлы.
- Provider status: без секретов, только имя провайдера/модели и флаг configured.

Эндпоинты
- POST /api/preview
  - Request: { "diff": string }
  - Success 200: { "redacted": string, "redactions_count": integer (>=0) }
  - Errors: 422 UNPROCESSABLE_CONTENT; 413 CONTENT_TOO_LARGE

- POST /api/reviews
  - Request: { "diff": string }
  - Success 200: { "summary": string, "risks": Array<{ file?: string, line?: number, evidence?: string, risk: string }>, "checks": Array<string> } (≤3 risks)
  - Errors: 422 UNPROCESSABLE_CONTENT; 413 CONTENT_TOO_LARGE; 502 LLM_UPSTREAM_ERROR; 503 PROVIDER_NOT_CONFIGURED

- GET /api/provider
  - Success 200: { "provider": "VseLLM", "model": string, "configured": boolean }

Ограничения и безопасность
- Лимит: 20000 Unicode code points.
- Редакция секретов: PEM, sk-*/ghp_*, JWT (eyJ… header), PASSWORD/SECRET/TOKEN/KEY (quoted/unquoted), AWS_*.
- Логи/ответы: ключи и сырые diff не попадают в логи/ответы; только метаданные.
- Таймаут LLM: ≤90s; без повторов; неподдерживаемые параметры (temperature, max_tokens) не отправляются.
- Prompt: на русском; diff включается как данные; запросить JSON‑ответ с полями summary/risks/checks.

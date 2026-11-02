Спецификация логики (after) — Redaction в POST /api/reviews (согласовано)

Endpoint и контракт
- POST /api/reviews
- Content-Type: application/json
- Request: { "diff": string } — обязательный параметр
- Лимит: длина diff ≤ 20000 символов (Unicode code points)
- Success 200:
  {
    "summary": string,
    "risks": [ { "file"?: string, "line"?: number, "evidence"?: string, "risk": string } ],
    "checks": [ string ]
  }
- Errors (единый формат): { "error": { "code": string, "message": string } }
  - 422 UNPROCESSABLE_CONTENT — отсутствует/нестроковый diff, невалидный JSON
  - 413 CONTENT_TOO_LARGE — длина diff > 20000 символов
  - 502 LLM_UPSTREAM_ERROR — эмуляция сбоя/таймаута заглушки

Redaction и безопасность
- Редакция секретов выполняется до логирования и до передачи в заглушку.
- Заменяем на "[REDACTED]" по распространённым паттернам:
  - PEM private key блоки (между BEGIN/END)
  - Токены/ключи: sk-*, ghp_*, JWT‑подобные (header.payload.signature)
  - Пары PASSWORD=/SECRET=/TOKEN=/KEY= (без учёта регистра)
  - AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY (значения)
- Ограничение: детерминированные regex не покрывают все возможные секреты; редактирование закрывает типичные случаи.
- Сырые diff и секреты не логируются и не возвращаются в ответе; заглушка получает только redacted diff.

Stub (LLM)
- Детерминированная заглушка на основе redacted diff.
- Эмуляция таймаута/сбоя по флагу (напр., "STUB_TIMEOUT") → 502 с кодом LLM_UPSTREAM_ERROR.

Acceptance Criteria
1) 200: корректный diff ≤20000; секреты редактируются; в ответе summary/risks≤3/checks; нет утечки секретов.
2) 422: отсутствует/нестроковый diff → заглушка не вызывается.
3) 413: diff длиной >20000 → заглушка не вызывается.
4) 502: эмуляция таймаута → контролируемая ошибка; нет утечки секретов; логов с сырым diff нет.

Примечания
- Пустая строка/whitespace diff: считается невалидным (422 UNPROCESSABLE_CONTENT).
- UI не отображает исходный diff; только summary/risks/checks.

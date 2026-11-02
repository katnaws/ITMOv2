Логическая спецификация v2 (before) — выдержка для UI

Опорный контракт (для согласования)
- GET /api/provider → { provider: 'VseLLM', model: string, configured: boolean }
- POST /api/preview { diff: string } → { redacted: string, redactions_count: integer ≥ 0 }
- POST /api/reviews { diff: string } → { summary: string, risks: Array<{ file?: string, line?: number, evidence?: string, risk: string }>, checks: Array<string> }

Ошибки
- 422 { error: { code: 'UNPROCESSABLE_CONTENT', message: string } }
- 413 { error: { code: 'CONTENT_TOO_LARGE', message: string } }
- 502 { error: { code: 'LLM_UPSTREAM_ERROR', message: string } }
- 503 { error: { code: 'PROVIDER_NOT_CONFIGURED', message: string } }

Правила
- Лимит 20000 Unicode code points.
- Сервер повторно чистит diff перед внешним вызовом review.
- Внешние сервисы получают только очищенный diff.

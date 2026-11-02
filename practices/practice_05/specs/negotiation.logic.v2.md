# Negotiation (Logic v2) — Preview + Real Review

Context
- UI proposes:
  - POST /api/preview { diff } -> { redacted, redactions_count }
  - POST /api/reviews { diff } -> { summary, risks<=3, checks }
  - GET /api/provider -> { provider: 'VseLLM', model: string, configured: bool }
  - Errors: 422/413; review: 502; 503 PROVIDER_NOT_CONFIGURED

Logic agreement
- Accept as proposed with clarifications:
  - Server always re-applies redaction before LLM.
  - Provider status excludes any secrets; only provider/model/configured.
  - 90s timeout; no retries; no unsupported params.
  - Preview never calls network.

Open questions to UI
- Do you want preview to show diff line numbers preserved or a flat text is enough? (default: preserve as-is with [REDACTED] substitutions)
- Should /api/provider be polled or fetched on demand? (default: on demand)

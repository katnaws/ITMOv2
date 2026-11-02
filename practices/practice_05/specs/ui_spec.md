Title: UI specification — Reviews endpoint client

Goal
- Provide a minimal client-facing contract for submitting a diff for review and viewing AI output without exposing secrets or raw diffs.

Screens and actions
- Action: Submit for review
  - Input: JSON body with field diff (string)
  - Success state: shows summary, risks (≤3), and checks returned by the server
  - Error states:
    - 422 Unprocessable Content when diff is missing or not a string
    - 413 Content Too Large when diff length > 20000
    - 502 Upstream error when AI provider is unavailable (not triggered by the current stub)

Constraints and rules
- UI must not render raw unredacted diffs or any secret values.
- If previewing content, only redacted text is allowed.
- The UI must surface at most three risks.

Out of scope
- Authentication, rate limits, persistence, or any client-side caching.

Contract (shared)
- Request: POST /api/reviews with JSON { "diff": string }
- Response (success): { "summary": string, "risks": Array<Risk>, "checks": Array<string> }
  - Risk: { file?: string, line?: number, evidence?: string, risk: string }

Acceptance criteria (UI)
- When the server returns a success response, the UI renders summary, ≤3 risks, and checks.
- The UI never displays secret content; placeholders like [REDACTED] may appear instead.
- On 422/413/502, the UI renders the corresponding error state without leaking input.

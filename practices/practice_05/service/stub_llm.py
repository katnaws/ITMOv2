class StubLLMError(Exception):
    pass


def review(redacted_diff: str):
    if "STUB_TIMEOUT" in redacted_diff:
        raise StubLLMError("upstream timeout")
    # Deterministic result based on content characteristics
    risks = []
    checks = []
    summary = "Review completed"
    if "[REDACTED]" in redacted_diff:
        risks.append({"risk": "Secrets were present and redacted"})
        checks.append("secrets_redacted")
    else:
        checks.append("no_secrets_detected")
    # Cap risks to at most 3 (already small)
    return {"summary": summary, "risks": risks[:3], "checks": checks}

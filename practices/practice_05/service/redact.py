import re


PEM_BLOCK_RE = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
    re.MULTILINE,
)

# Heuristic for JWT: typical header is a base64url of a JSON object starting with '{',
# which often encodes to a string starting with 'eyJ'. This avoids matching domains.
JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
PREFIX_TOKEN_RE = re.compile(r"\b(?:sk-[A-Za-z0-9_-]+|ghp_[A-Za-z0-9]+)\b")
# Support quoted values with spaces or unquoted tokens.
ENV_PAIR_RE = re.compile(
    r"\b(?P<name>(?:PASSWORD|SECRET|TOKEN|KEY))\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))",
    re.IGNORECASE,
)
AWS_ACCESS_RE = re.compile(r"\b(?P<name>AWS_ACCESS_KEY_ID)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))")
AWS_SECRET_RE = re.compile(r"\b(?P<name>AWS_SECRET_ACCESS_KEY)\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s]+))")


def _replace_env_pairs(text: str) -> str:
    def repl(m):
        name = m.group("name")
        return f"{name.upper()}=[REDACTED]"

    text = ENV_PAIR_RE.sub(repl, text)
    # Normalize AWS pairs to [REDACTED]
    def repl_aws(m):
        name = m.group("name")
        return f"{name}=[REDACTED]"

    text = AWS_ACCESS_RE.sub(repl_aws, text)
    text = AWS_SECRET_RE.sub(repl_aws, text)
    return text


def redact_diff(diff: str) -> str:
    # Replace PEM blocks entirely
    redacted = PEM_BLOCK_RE.sub("[REDACTED]", diff)
    # Replace tokens and JWTs
    redacted = PREFIX_TOKEN_RE.sub("[REDACTED]", redacted)
    redacted = JWT_RE.sub("[REDACTED]", redacted)
    # Replace env-like pairs
    redacted = _replace_env_pairs(redacted)
    return redacted


def redact_and_count(diff: str):
    """Single-pass redaction pipeline with count; idempotent on [REDACTED]."""
    # First run the same transformations as redact_diff
    redacted = redact_diff(diff)
    # Count occurrences of [REDACTED] markers introduced by pipeline
    # Ensure idempotence: repeated call doesn't increase count
    count = redacted.count("[REDACTED]") - diff.count("[REDACTED]")
    if count < 0:
        count = 0
    return redacted, count

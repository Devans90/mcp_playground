import re

_PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # US SSN example (placeholder)
    re.compile(r"\b\d{16}\b"),             # crude card number pattern
]

def redact_pii(text: str) -> str:
    """
    Redact simple PII patterns. Extend as needed.
    """
    out = text
    for p in _PII_PATTERNS:
        out = p.sub("[REDACTED]", out)
    return out

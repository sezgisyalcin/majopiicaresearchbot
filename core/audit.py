from __future__ import annotations
from dataclasses import dataclass
from urllib.parse import urlparse
from core.policy import ALLOWED_SOURCE_KINDS, BLOCKED_HOST_CONTAINS

@dataclass(frozen=True)
class Source:
    label: str
    url: str
    kind: str

def _host(url: str) -> str:
    return (urlparse(url).hostname or "").lower()

def is_blocked(url: str) -> bool:
    h = _host(url)
    return any(b in h for b in BLOCKED_HOST_CONTAINS)

def audit_sources(sources: list[Source]) -> tuple[bool, list[str]]:
    errors: list[str] = []
    for s in sources:
        if not s.url.startswith(("https://","http://")):
            errors.append(f"Invalid URL scheme: {s.url}")
        if is_blocked(s.url):
            errors.append(f"Blocked source domain: {s.url}")
        if s.kind not in ALLOWED_SOURCE_KINDS:
            errors.append(f"Invalid source kind: {s.kind}")
        if not s.label or len(s.label) < 3:
            errors.append("Missing or too-short source label.")
    return (len(errors) == 0, errors)

def sources_block(sources: list[Source]) -> str:
    ok, _ = audit_sources(sources)
    if not ok:
        return "Sources: (withheld — audit failed)"
    return "Sources:\n" + "\n".join([f"- {s.label}: {s.url}" for s in sources])

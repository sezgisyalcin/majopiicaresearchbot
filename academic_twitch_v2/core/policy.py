from urllib.parse import urlparse

BLOCKED_DOMAINS = {
    "wikipedia.org", "wikimedia.org", "wikidata.org", "dbpedia.org",
}

def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""

def is_blocked(url: str) -> bool:
    d = _domain(url)
    return any(b in d for b in BLOCKED_DOMAINS)

def is_allowed(url: str, allowlist_domains: set[str]) -> bool:
    if not url or is_blocked(url):
        return False
    d = _domain(url)
    return any(ad in d for ad in allowlist_domains)

def clamp(s: str, n: int = 450) -> str:
    s = (s or "").strip()
    if len(s) <= n:
        return s
    return s[:n-1] + "…"

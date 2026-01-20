from __future__ import annotations

from typing import Dict, Iterable, List, Set
from urllib.parse import urlparse

DOMAIN_TYPE_MAP = {
    "metmuseum.org": "Museum",
    "moma.org": "Museum",
    "vam.ac.uk": "Museum",
    "britishmuseum.org": "Museum",
    "tate.org.uk": "Museum",
    "louvre.fr": "Museum",
    "uffizi.it": "Museum",
    "vatican.va": "Museum",
    "bfi.org.uk": "Archive/Institute",
    "jpf.go.jp": "Foundation/Government",
}

def _host(url: str) -> str:
    try:
        h = urlparse(url).netloc.lower()
        if h.startswith("www."):
            h = h[4:]
        return h
    except Exception:
        return ""

def classify_source(url: str) -> str:
    host = _host(url)
    if not host:
        return "Institution"
    if host.endswith(".edu") or ".ac." in host:
        return "University"
    for dom, typ in DOMAIN_TYPE_MAP.items():
        if host == dom or host.endswith("." + dom):
            return typ
    return "Institution"

def extract_source_types(sources: Iterable[Dict]) -> List[str]:
    types: Set[str] = set()
    for s in sources or []:
        url = str(s.get("url",""))
        types.add(classify_source(url))
    order = ["University", "Museum", "Archive/Institute", "Foundation/Government", "Institution"]
    return [t for t in order if t in types]

def format_sources(sources: Iterable[Dict], limit: int = 6) -> str:
    lines: List[str] = []
    for s in (sources or [])[:limit]:
        label = str(s.get("label","")).strip()
        url = str(s.get("url","")).strip()
        if not label and not url:
            continue
        if label and url:
            lines.append(f"• {label}: {url}")
        elif url:
            lines.append(f"• {url}")
        else:
            lines.append(f"• {label}")
    return "\n".join(lines) if lines else ""

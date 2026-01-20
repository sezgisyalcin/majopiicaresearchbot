import json, random
from typing import Any, Dict, List, Optional, Tuple
from core.audit import Source, audit_sources
from core.util import clamp_mode

def load(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_one(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return random.choice(items) if items else None

def format_artist(a: Dict[str, Any], mode: str="short") -> Tuple[str, str, list[Source]]:
    mode = clamp_mode(mode)
    title = f"ITALIAN ARTIST — {a.get('name','—').upper()}"
    period = a.get("period","—")
    domain = a.get("domain","—")
    one_line = a.get("one_line","—")
    srcs = [Source(s["label"], s["url"], s["kind"]) for s in a.get("institutional_sources", [])]

    ok, _ = audit_sources(srcs)
    if not ok:
        srcs = []

    if mode == "short":
        body = f"Period: {period}\nDomain: {domain}\nNote: {one_line}"
    elif mode == "extended":
        body = (
            f"Period: {period}\nDomain: {domain}\n\n"
            f"Academic note: {one_line}\n\n"
            "Use museum research portals and university catalogues for primary descriptions and scholarly context."
        )
    else:
        body = (
            "Research routing (academic-only)\n"
            f"• Period: {period}\n"
            f"• Domain: {domain}\n"
            f"• Framing note: {one_line}\n\n"
            "Method:\n"
            "1) Start with museum research portals and university catalogues.\n"
            "2) Prefer peer-reviewed publications and institutional archives.\n"
            "3) Avoid non-institutional summaries."
        )
    return title, body, srcs

import json, random
from typing import Any, Dict, List, Optional, Tuple
from core.util import norm, clamp_mode

VALID_PERIODS = {"medieval","renaissance","baroque","classical","romantic","modern","contemporary"}

def load(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [c for c in data if c.get("nationality") == "Italian"]

def filter_list(items: List[Dict[str, Any]], name: Optional[str]=None, period: Optional[str]=None,
                berklee_modern: bool=False, oxbridge: bool=False) -> List[Dict[str, Any]]:
    out = items[:]
    if name:
        q = norm(name)
        out = [c for c in out if q in norm(c.get("name",""))]
    if period:
        p = norm(period)
        if p not in VALID_PERIODS:
            return []
        out = [c for c in out if norm(c.get("period","")) == p]

    if berklee_modern:
        out = [c for c in out if norm(c.get("period","")) in {"modern","contemporary"}]
        out = [c for c in out if any("berklee" in norm(s.get("institution","")) for s in c.get("sources", []))]

    if oxbridge:
        def has_oxbridge(c):
            insts = " ".join([norm(s.get("institution","")) for s in c.get("sources", [])])
            return ("oxford" in insts) or ("cambridge" in insts)
        out = [c for c in out if has_oxbridge(c)]

    return out

def pick_one(items: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return random.choice(items) if items else None

def format_item(c: Dict[str, Any], mode: str="short") -> Tuple[str, str]:
    mode = clamp_mode(mode)
    years = f" ({c['born']}–{c['died']})" if c.get("born") and c.get("died") else ""
    title = f"ITALIAN COMPOSER — {c['name'].upper()}{years}"
    period = c.get("period","—").title()
    focus = c.get("focus", [])
    works = c.get("core_works", [])
    sources = c.get("sources", [])

    if mode == "short":
        body = (
            f"Period: {period}\n"
            f"Focus: {', '.join(focus[:3]) if focus else '—'}\n"
            f"Core works: {', '.join(works[:2]) if works else '—'}\n"
            f"Institutional labels: {', '.join([s.get('institution','').split('·')[0].strip() for s in sources[:2]]) if sources else '—'}"
        )
        return title, body

    if mode == "extended":
        body = (
            f"Period: {period}\n\n"
            "Overview\n"
            f"- Focus areas: {', '.join(focus) if focus else '—'}\n"
            f"- Representative works: {', '.join(works[:3]) if works else '—'}\n\n"
            "Institutional references\n" +
            "\n".join([f"• {s.get('institution','—')}" for s in sources[:5]])
        )
        return title, body

    body = (
        "Academic notes\n"
        f"• Period: {period}\n"
        f"• Analytical themes: {', '.join(focus) if focus else '—'}\n"
        f"• Works commonly cited in scholarship: {', '.join(works) if works else '—'}\n\n"
        "Verified institutional references\n" +
        "\n".join([f"• {s.get('institution','—')} — {s.get('title','—')} ({s.get('type','—')})" for s in sources[:10]])
    )
    return title, body

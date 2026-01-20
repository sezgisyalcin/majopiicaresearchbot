from core.util import norm, clamp_mode
from data.italy_figures import ITALIAN_PAINTERS, ITALIAN_ARCHITECTS, ITALIAN_PHILOSOPHERS

def _pick(items, name=None, period=None):
    qn = norm(name) if name else ""
    qp = norm(period) if period else ""
    out = []
    for it in items:
        if qn and qn not in norm(it.name):
            continue
        if qp and qp != norm(it.period):
            continue
        out.append(it)
    return out

def format_list(title, items, name=None, period=None, mode="short"):
    mode = clamp_mode(mode)
    matches = _pick(items, name=name, period=period)
    lines = [f"{title} ({mode})"]
    if not matches:
        lines.append("No match found in the curated core list. Use /sources for institutional references.")
        return "\n".join(lines)
    if mode == "short":
        for it in matches[:10]:
            lines.append(f"- {it.name} · {it.period}")
    elif mode == "extended":
        for it in matches[:10]:
            lines.append(f"- {it.name} · {it.period} — {it.notes}")
    else:
        for it in matches[:15]:
            lines.append(f"- {it.name} · {it.period} — {it.notes}")
        lines.append("Research routing: consult institutional catalogues and scholarly databases under /sources.")
    return "\n".join(lines)

def painters(name=None, period=None, mode="short"):
    return format_list("ITALIAN PAINTERS", ITALIAN_PAINTERS, name, period, mode)

def architects(name=None, period=None, mode="short"):
    return format_list("ITALIAN ARCHITECTS", ITALIAN_ARCHITECTS, name, period, mode)

def philosophers(name=None, period=None, mode="short"):
    return format_list("ITALIAN PHILOSOPHERS", ITALIAN_PHILOSOPHERS, name, period, mode)

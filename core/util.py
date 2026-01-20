import re
def norm(s: str | None) -> str:
    return re.sub(r"\s+"," ", (s or "").strip().lower())
def clamp_mode(mode: str | None) -> str:
    m = norm(mode) or "short"
    return m if m in {"short","extended","research"} else "short"

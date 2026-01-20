from __future__ import annotations
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import requests

DEFAULT_TIMEOUT = 14
BASE = "https://api.nobelprize.org/2.1/nobelPrizes"

# Cache: key -> (ts, payload)
_CACHE: dict[str, tuple[float, dict]] = {}

@dataclass(frozen=True)
class NobelLaureate:
    name: str
    motivation: str

@dataclass(frozen=True)
class NobelPrize:
    year: int
    category_en: str
    category_code: str
    date_awarded: str
    laureates: List[NobelLaureate]

SCIENCE_CODES = {"phy", "che", "med", "eco"}
LITERATURE_CODE = "lit"

def _ua() -> str:
    return os.getenv("NOBEL_USER_AGENT") or "AcademicDiscordBot/1.0 (contact: set NOBEL_USER_AGENT)"

def _ttl() -> int:
    try:
        return int(os.getenv("NOBEL_CACHE_TTL_SECONDS") or "21600")  # 6 hours default
    except Exception:
        return 21600

def _get(params: dict) -> dict:
    # Simple in-memory cache to reduce API calls on Railway.
    key = "&".join([f"{k}={params[k]}" for k in sorted(params.keys())])
    now = time.time()
    ttl = _ttl()
    if key in _CACHE and (now - _CACHE[key][0]) < ttl:
        return _CACHE[key][1]

    r = requests.get(BASE, params=params, timeout=DEFAULT_TIMEOUT, headers={"User-Agent": _ua()})
    r.raise_for_status()
    data = r.json()
    _CACHE[key] = (now, data)
    return data

def _code_from_links(prize_obj: dict) -> str:
    # The API provides href like https://api.nobelprize.org/2/nobelPrize/phy/2023
    links = prize_obj.get("links") or []
    for l in links:
        href = (l.get("href") or "")
        m = href.split("/nobelPrize/")
        if len(m) == 2:
            tail = m[1]  # e.g. phy/2023
            code = tail.split("/")[0].strip()
            if code:
                return code
    # Fallback: infer from categoryFullName
    cat = ((prize_obj.get("categoryFullName") or {}).get("en") or "").lower()
    if "physics" in cat: return "phy"
    if "chemistry" in cat: return "che"
    if "physiology" in cat or "medicine" in cat: return "med"
    if "literature" in cat: return "lit"
    if "economic" in cat: return "eco"
    if "peace" in cat: return "pea"
    return "unk"

def _parse_prizes(payload: dict) -> List[NobelPrize]:
    prizes = []
    for p in payload.get("nobelPrizes") or []:
        year_s = p.get("awardYear") or "0"
        try:
            year = int(year_s)
        except Exception:
            continue
        code = _code_from_links(p)
        cat_en = ((p.get("category") or {}).get("en") or code.upper())
        date_awarded = p.get("dateAwarded") or ""
        laureates = []
        for l in p.get("laureates") or []:
            name = ((l.get("fullName") or {}).get("en") or (l.get("knownName") or {}).get("en") or "").strip()
            if not name:
                continue
            motivation = ((l.get("motivation") or {}).get("en") or "").strip()
            laureates.append(NobelLaureate(name=name, motivation=motivation))
        prizes.append(NobelPrize(year=year, category_en=cat_en, category_code=code, date_awarded=date_awarded, laureates=laureates))
    return prizes

def fetch_year(year: int) -> List[NobelPrize]:
    payload = _get({"nobelPrizeYear": year})
    return _parse_prizes(payload)

def latest_available_year(start_year: int, predicate) -> Optional[int]:
    y = start_year
    for _ in range(20):  # look back up to 20 years
        prizes = fetch_year(y)
        if any(predicate(p) for p in prizes):
            return y
        y -= 1
    return None

def science_winners(year: int) -> List[NobelPrize]:
    prizes = fetch_year(year)
    return [p for p in prizes if p.category_code in SCIENCE_CODES]

def literature_winners(year: int) -> List[NobelPrize]:
    prizes = fetch_year(year)
    return [p for p in prizes if p.category_code == LITERATURE_CODE]

def format_prize_block(p: NobelPrize, max_laureates: int = 6) -> str:
    names = [l.name for l in p.laureates][:max_laureates]
    line = ", ".join(names) if names else "(no laureates listed)"
    return f"**{p.category_en} ({p.year})** — {line}"

def format_motivations(p: NobelPrize, max_items: int = 3) -> str:
    out = []
    for l in p.laureates[:max_items]:
        if l.motivation:
            out.append(f"• {l.name}: {l.motivation}")
        else:
            out.append(f"• {l.name}")
    return "\n".join(out) if out else "—"

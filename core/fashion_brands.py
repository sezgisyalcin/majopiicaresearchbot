from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class FashionBrand:
    name: str
    founded_year: Optional[int]
    region: str
    hq_city: str
    website: str
    one_liner: str

def load_dataset(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_all(path: str) -> List[FashionBrand]:
    data = load_dataset(path)
    out: List[FashionBrand] = []
    for r in data.get("items") or []:
        out.append(FashionBrand(
            name=str(r["name"]),
            founded_year=int(r["founded_year"]) if r.get("founded_year") is not None else None,
            region=str(r.get("region") or "unknown").lower(),
            hq_city=str(r.get("hq_city") or ""),
            website=str(r.get("website") or ""),
            one_liner=str(r.get("one_liner") or "").strip(),
        ))
    return out

def timeline(path: str, from_year: Optional[int]=None, to_year: Optional[int]=None) -> List[FashionBrand]:
    rows = [b for b in list_all(path) if b.founded_year is not None]
    if from_year is not None:
        rows = [b for b in rows if b.founded_year >= from_year]
    if to_year is not None:
        rows = [b for b in rows if b.founded_year <= to_year]
    return sorted(rows, key=lambda b: (b.founded_year or 9999, b.name.lower()))

def by_region(path: str, region: str) -> List[FashionBrand]:
    reg = (region or "").strip().lower()
    return sorted([b for b in list_all(path) if b.region == reg], key=lambda b: b.name.lower())

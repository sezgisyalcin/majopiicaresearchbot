from __future__ import annotations
import json, random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class GameCardSystem:
    name: str
    type: str  # physical|digital
    publisher: str
    official_url: str

def load_dataset(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_all(path: str) -> List[GameCardSystem]:
    data = load_dataset(path)
    out: List[GameCardSystem] = []
    for r in data.get("items") or []:
        out.append(GameCardSystem(
            name=str(r["name"]),
            type=str(r.get("type") or "unknown").lower(),
            publisher=str(r.get("publisher") or ""),
            official_url=str(r.get("official_url") or ""),
        ))
    return out

def pick_one(path: str, kind: Optional[str]=None) -> GameCardSystem:
    items = list_all(path)
    if kind:
        k = kind.strip().lower()
        items = [i for i in items if i.type == k]
    if not items:
        raise ValueError("No matching items.")
    return random.choice(items)

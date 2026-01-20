from __future__ import annotations
import json, random
from typing import Any, Dict, List, Optional

def load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_periods(path: str) -> List[Dict[str, Any]]:
    return list(load(path).get("items", []))

def pick_period(path: str, key: Optional[str]=None) -> Dict[str, Any]:
    items = list_periods(path)
    if key:
        k = key.strip().lower()
        for it in items:
            if (it.get("key") or "").lower() == k:
                return it
        raise ValueError("Unknown period key")
    return random.choice(items)

from __future__ import annotations
import json, random
from typing import Any, Dict, Optional

def load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick(path: str, author: Optional[str]=None) -> Dict[str, Any]:
    items = load(path).get("items", [])
    if author:
        a = author.strip().lower()
        items = [i for i in items if str(i.get("author","")).lower() == a]
    if not items:
        raise ValueError("No matching items")
    return random.choice(items)

from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional

def _load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_technique(path: str, tag: Optional[str] = None) -> Dict[str, Any]:
    data = _load(path)
    items: List[Dict[str, Any]] = list(data.get("items", []))
    if tag:
        t = tag.strip().lower()
        items = [i for i in items if t in [x.lower() for x in (i.get("tags") or [])]]
    if not items:
        raise ValueError("No matching techniques")
    return random.choice(items)

def list_tags(path: str) -> List[str]:
    data = _load(path)
    tags = set()
    for i in data.get("items", []):
        for t in (i.get("tags") or []):
            tags.add(str(t))
    return sorted(tags)

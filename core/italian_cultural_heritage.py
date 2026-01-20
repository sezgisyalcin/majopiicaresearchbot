from __future__ import annotations
import json, random
from typing import Dict, Any

def load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_unesco(path: str) -> Dict[str, Any]:
    items = [i for i in load(path).get("items", []) if i.get("unesco")]
    if not items:
        raise ValueError("No UNESCO items available.")
    return random.choice(items)

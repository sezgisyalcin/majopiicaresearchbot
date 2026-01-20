from __future__ import annotations
import json, random
from typing import Any, Dict

def load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_astronomer(path: str) -> Dict[str, Any]:
    items = (load(path).get("astronomers") or [])
    if not items:
        raise ValueError("No astronomers in dataset.")
    return random.choice(items)

def pick_history(path: str) -> Dict[str, Any]:
    items = (load(path).get("history") or [])
    if not items:
        raise ValueError("No history entries in dataset.")
    return random.choice(items)

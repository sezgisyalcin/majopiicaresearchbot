from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional

from utils.io import load_json


def pick_random_from_registry(reg_path: str, key: str) -> Dict[str, Any]:
    reg = load_json(reg_path)
    items: List[Dict[str, Any]] = reg.get(key, [])
    if not items:
        raise RuntimeError(f"Registry '{reg_path}' has no items under key '{key}'.")
    return random.choice(items)


def pick_random_from_jsonl(jsonl_path: str, *, predicate: Optional[callable] = None) -> Dict[str, Any]:
    """Pick a random JSON object from a JSONL file.

    Uses reservoir sampling so it works for large files without loading them fully.
    """
    chosen: Optional[Dict[str, Any]] = None
    n = 0
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if predicate is not None and not predicate(obj):
                continue
            n += 1
            if random.randint(1, n) == 1:
                chosen = obj

    if chosen is None:
        raise RuntimeError(f"No eligible items found in JSONL: {jsonl_path}")
    return chosen

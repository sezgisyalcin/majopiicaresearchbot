from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional


Predicate = Callable[[Dict[str, Any]], bool]


def pick_random(items: List[Dict[str, Any]], *, predicate: Optional[Predicate] = None) -> Dict[str, Any]:
    pool = items if predicate is None else [x for x in items if predicate(x)]
    if not pool:
        raise RuntimeError("No items matched the filter.")
    return random.choice(pool)


def pick_random_jsonl(path: Path, *, predicate: Optional[Predicate] = None) -> Dict[str, Any]:
    """Pick a random JSON object from a JSONL file using reservoir sampling.

    This supports very large datasets (e.g., UNESCO WHC JSONL with 1k+ sites)
    without loading all records into memory.
    """
    chosen: Optional[Dict[str, Any]] = None
    n = 0

    with path.open("r", encoding="utf-8") as f:
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
        raise RuntimeError(f"No eligible items found in JSONL: {path}")
    return chosen

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_registry_items(path: Path, key: str) -> List[Dict[str, Any]]:
    obj = load_json(path)
    items = obj.get(key, []) if isinstance(obj, dict) else []
    if not isinstance(items, list):
        raise RuntimeError(f"Registry '{path}' key '{key}' is not a list.")
    return items


def iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    """Stream JSON objects from JSONL."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def jsonl_exists(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def load_optional_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    return load_json(path)

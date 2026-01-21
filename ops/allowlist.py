import json, os
from typing import Set

STORE = os.path.join(os.path.dirname(__file__), "allowlist.json")

def _load() -> Set[int]:
    if not os.path.exists(STORE):
        return set()
    with open(STORE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(int(x) for x in data.get("user_ids", []))

def _save(ids: Set[int]) -> None:
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump({"user_ids": sorted(list(ids))}, f, indent=2)

def is_allowed(user_id: int) -> bool:
    ids = _load()
    return user_id in ids if ids else True

def add(user_id: int) -> None:
    ids = _load()
    ids.add(int(user_id))
    _save(ids)

def remove(user_id: int) -> None:
    ids = _load()
    if int(user_id) in ids:
        ids.remove(int(user_id))
    _save(ids)

def list_ids() -> list[int]:
    return sorted(list(_load()))

import json
from typing import Dict, List, Tuple

def load_terms(path: str) -> Dict[str, str]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def list_terms(path: str) -> List[str]:
    return sorted(load_terms(path).keys())

def explain(path: str, term: str) -> Tuple[str, str] | None:
    data = load_terms(path)
    key = term.strip().lower()
    # normalize spaces/underscores/hyphens lightly
    key = key.replace(" ", "-").replace("_", "-")
    if key in data:
        return key, data[key]
    return None

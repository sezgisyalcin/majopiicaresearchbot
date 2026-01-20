from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

def load_glossary(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_term(glossary: Dict[str, Any], query: str) -> Optional[Dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q:
        return None
    for t in glossary.get("terms", []):
        term = str(t.get("term","")).strip().lower()
        if term == q:
            return t
    for t in glossary.get("terms", []):
        term = str(t.get("term","")).strip().lower()
        if q in term:
            return t
    return None

def list_terms(glossary: Dict[str, Any], limit: int = 25) -> List[str]:
    terms = [str(t.get("term","")).strip() for t in glossary.get("terms", []) if t.get("term")]
    terms = [t for t in terms if t]
    terms.sort()
    return terms[:limit]

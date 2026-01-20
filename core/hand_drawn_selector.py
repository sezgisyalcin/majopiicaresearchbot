from __future__ import annotations

import json
import random
from typing import Any, Dict, List, Optional, Tuple

def _load(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_pair(path: str, tag: Optional[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    data = _load(path)
    techniques: List[Dict[str, Any]] = list(data.get("techniques", []))
    tools: List[Dict[str, Any]] = list(data.get("tools", []))

    if tag:
        t = tag.strip().lower()
        techniques = [x for x in techniques if t in [y.lower() for y in (x.get("tags") or [])]]
        tools_tagged = [x for x in tools if t in [y.lower() for y in (x.get("tags") or [])]]
        if tools_tagged:
            tools = tools_tagged

    if not techniques or not tools:
        raise ValueError("No matching items")

    tech = random.choice(techniques)

    rec = [r for r in (tech.get("recommended_tools") or [])]
    tool = None
    if rec:
        by_id = {t["id"]: t for t in tools if "id" in t}
        candidates = [by_id[r] for r in rec if r in by_id]
        if candidates:
            tool = random.choice(candidates)

    if tool is None:
        tool = random.choice(tools)

    return tech, tool

def list_tags(path: str) -> List[str]:
    data = _load(path)
    tags = set()
    for arr in (data.get("techniques", []), data.get("tools", [])):
        for i in arr:
            for t in (i.get("tags") or []):
                tags.add(str(t))
    return sorted(tags)

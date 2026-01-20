from __future__ import annotations

from typing import Any, Dict, List


def filter_verified_official_items(reg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return items that are active and marked as verified (PASS).

    Expected registry format:
      {
        "items": [
          {
            "is_active": true,
            "verification": {"status": "PASS"},
            ...
          }
        ]
      }
    """
    items = reg.get("items", []) if isinstance(reg, dict) else []
    out: List[Dict[str, Any]] = []
    for i in items:
        if not isinstance(i, dict):
            continue
        if i.get("is_active") is not True:
            continue
        status = (i.get("verification") or {}).get("status")
        if status == "PASS":
            out.append(i)
    return out

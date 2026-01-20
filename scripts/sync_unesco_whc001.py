#!/usr/bin/env python3
"""Sync UNESCO World Heritage data into JSONL (ID-based) using a pinned CKAN resource.

Design goals
------------
1) **No runtime scraping**: the bot reads local JSON/JSONL only.
2) **Pinning for stability**: endpoint + resource_id are defined in `config/unesco_whc.json`.
3) **CI-friendly**: deterministic output ordering and a lock file for change detection.

Configuration
-------------
Edit `config/unesco_whc.json` and set:
  - ckan_datastore_search_url
  - resource_id (CKAN resource UUID)

Usage
-----
python scripts/sync_unesco_whc001.py --config config/unesco_whc.json

Optional:
  --limit 1000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse

import requests


@dataclass(frozen=True)
class SyncConfig:
    ckan_datastore_search_url: str
    resource_id: str
    page_size: int
    limit: int
    output_jsonl: Path
    output_index: Path
    lock_file: Path
    pin_mode: str
    expected_domain: Optional[str]
    require_https: bool
    allow_redirects: bool


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def _safe_get(d: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _normalize_record(r: Dict[str, Any]) -> Dict[str, Any]:
    """Map a raw record into the bot-friendly schema.

    Field names may vary; we normalize defensively.
    """
    wh_id = r.get("id") or r.get("wh_id") or r.get("site_id") or r.get("UNESCO_ID") or r.get("whc_id")
    name = r.get("name") or r.get("site") or r.get("site_name") or r.get("property")
    country = r.get("country") or r.get("states") or r.get("states_parties") or r.get("state_party")
    category = r.get("category") or r.get("type") or r.get("kind")
    year = r.get("year_inscribed") or r.get("date_inscribed") or r.get("inscription_year")

    criteria = r.get("criteria")
    if isinstance(criteria, str):
        cleaned = criteria.replace("(", " ").replace(")", " ").replace(",", " ")
        parts = [p.strip() for p in cleaned.split() if p.strip()]
        criteria_list = parts
    elif isinstance(criteria, list):
        criteria_list = [str(x) for x in criteria if str(x).strip()]
    else:
        criteria_list = []

    lat = r.get("lat") or r.get("latitude")
    lon = r.get("lon") or r.get("longitude")

    whc_url = r.get("whc_url") or r.get("url")
    if whc_url and "whc.unesco.org" not in str(whc_url):
        # Do not fabricate; keep only canonical WHC pages.
        whc_url = None

    return {
        "wh_id": wh_id,
        "name": name,
        "country": country,
        "category": category,
        "year_inscribed": year,
        "criteria": criteria_list,
        "lat": lat,
        "lon": lon,
        "whc_url": whc_url,
        "source": "UNESCO Datahub (CKAN datastore_search)",
    }


def _parse_config(config_path: Path) -> SyncConfig:
    raw = _load_json(config_path)
    out = raw.get("output", {}) if isinstance(raw, dict) else {}
    pin = raw.get("pinning", {}) if isinstance(raw, dict) else {}

    return SyncConfig(
        ckan_datastore_search_url=str(raw.get("ckan_datastore_search_url")),
        resource_id=str(raw.get("resource_id")),
        page_size=int(raw.get("page_size", 500)),
        limit=int(raw.get("limit", 0)),
        output_jsonl=Path(str(out.get("jsonl", "data/whc/whc_sites.jsonl"))),
        output_index=Path(str(out.get("index", "data/whc/whc_sites_index.json"))),
        lock_file=Path(str(raw.get("lock_file", "config/unesco_whc.lock.json"))),
        pin_mode=str(pin.get("mode", "strict")),
        expected_domain=pin.get("expected_domain"),
        require_https=bool(pin.get("require_https", True)),
        allow_redirects=bool(pin.get("allow_redirects", False)),
    )


def _validate_pinning(cfg: SyncConfig) -> None:
    parsed = urlparse(cfg.ckan_datastore_search_url)

    if cfg.require_https and parsed.scheme != "https":
        raise RuntimeError(f"Pinning violation: endpoint must be https: {cfg.ckan_datastore_search_url}")
    if cfg.expected_domain and parsed.netloc != cfg.expected_domain:
        raise RuntimeError(
            f"Pinning violation: endpoint domain must be {cfg.expected_domain}, got {parsed.netloc}"
        )
    if not cfg.ckan_datastore_search_url.endswith("/api/3/action/datastore_search"):
        raise RuntimeError(
            "Pinning violation: endpoint must be a CKAN datastore_search action URL ending with /api/3/action/datastore_search"
        )
    if not cfg.resource_id or cfg.resource_id.strip() == "":
        raise RuntimeError("Pinning violation: resource_id is empty")


def _enforce_lock(cfg: SyncConfig, *, lock_path: Path) -> Dict[str, Any]:
    if not lock_path.exists():
        return {}
    lock = _load_json(lock_path)
    pinned = (lock or {}).get("pinned", {}) if isinstance(lock, dict) else {}

    # If lock is still placeholder, do not enforce.
    lock_rid = str(pinned.get("resource_id") or "")
    lock_url = str(pinned.get("ckan_datastore_search_url") or "")
    if "REPLACE_WITH" in lock_rid or "REPLACE_WITH" in str(cfg.resource_id):
        return lock if isinstance(lock, dict) else {}

    if cfg.pin_mode == "strict":
        if lock_rid and lock_rid != cfg.resource_id:
            raise RuntimeError(
                f"Lock violation: resource_id changed. lock={lock_rid} config={cfg.resource_id}. "
                "Update config AND lock deliberately if this is intended."
            )
        if lock_url and lock_url != cfg.ckan_datastore_search_url:
            raise RuntimeError(
                f"Lock violation: endpoint URL changed. lock={lock_url} config={cfg.ckan_datastore_search_url}. "
                "Update config AND lock deliberately if this is intended."
            )

    return lock if isinstance(lock, dict) else {}


def _datastore_search(cfg: SyncConfig, *, offset: int) -> Dict[str, Any]:
    params = {
        "resource_id": cfg.resource_id,
        "limit": cfg.page_size,
        "offset": offset,
    }
    resp = requests.get(
        cfg.ckan_datastore_search_url,
        params=params,
        timeout=60,
        allow_redirects=cfg.allow_redirects,
    )
    resp.raise_for_status()
    return resp.json()


def _build_index(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    # Lightweight index: list of ids and name pairs for quick inspection.
    pairs = []
    for r in rows:
        wh_id = r.get("wh_id")
        name = r.get("name")
        if wh_id is None or not name:
            continue
        pairs.append({"wh_id": wh_id, "name": name})
    return {
        "count": len(rows),
        "ids": pairs,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/unesco_whc.json")
    ap.add_argument("--limit", type=int, default=None, help="Override config.limit (0 = no limit)")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    if not cfg_path.exists():
        print(f"Config not found: {cfg_path}", file=sys.stderr)
        return 2

    cfg = _parse_config(cfg_path)
    if args.limit is not None:
        cfg = SyncConfig(
            **{**cfg.__dict__, "limit": int(args.limit)}
        )

    try:
        _validate_pinning(cfg)
        lock = _enforce_lock(cfg, lock_path=cfg.lock_file)
    except Exception as e:
        print(f"[sync_unesco_whc001] configuration error: {e}", file=sys.stderr)
        return 2

    all_rows: List[Dict[str, Any]] = []
    offset = 0

    try:
        while True:
            payload = _datastore_search(cfg, offset=offset)
            records = _safe_get(payload, ["result", "records"], [])
            if not isinstance(records, list):
                raise RuntimeError("Unexpected response shape: result.records is not a list")

            for r in records:
                if not isinstance(r, dict):
                    continue
                norm = _normalize_record(r)
                if norm.get("wh_id") is None or not norm.get("name"):
                    continue
                all_rows.append(norm)
                if cfg.limit and len(all_rows) >= cfg.limit:
                    break

            if cfg.limit and len(all_rows) >= cfg.limit:
                break
            if len(records) < cfg.page_size:
                break
            offset += cfg.page_size

    except Exception as e:
        print(f"[sync_unesco_whc001] fetch failed: {e}", file=sys.stderr)
        return 3

    # Deterministic order to reduce diff churn
    all_rows.sort(key=lambda x: (str(x.get("wh_id")), str(x.get("name"))))

    # Write outputs
    _write_jsonl(cfg.output_jsonl, all_rows)
    _write_json(cfg.output_index, _build_index(all_rows))

    # Update lock
    now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    new_lock = {
        "name": "unesco_whc001",
        "pinned": {
            "ckan_datastore_search_url": cfg.ckan_datastore_search_url,
            "resource_id": cfg.resource_id,
        },
        "last_synced_utc": now_utc,
        "record_count": len(all_rows),
    }
    # Preserve optional notes
    if isinstance(lock, dict) and lock.get("notes"):
        new_lock["notes"] = lock.get("notes")
    _write_json(cfg.lock_file, new_lock)

    print(f"Wrote {len(all_rows)} records to {cfg.output_jsonl}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

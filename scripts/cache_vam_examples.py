#!/usr/bin/env python3
"""Cache V&A Collections examples (optional).

This script creates a lightweight local cache of V&A record URLs for use as
instrument examples. No API key is required for the public endpoint, but you
should keep row limits conservative.

Output format: JSONL (one record per line)

Usage
-----
python scripts/cache_vam_examples.py --config config/vam_collections.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def canonicalize_https(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("http://"):
        url = "https://" + url[len("http://") :]
    return url


@dataclass(frozen=True)
class Pins:
    base_url: str
    search_path: str
    out_path: str
    lock_path: str


def pins_from_config(cfg: Dict[str, Any]) -> Pins:
    base_url = canonicalize_https(str(cfg.get("base_url") or "https://api.vam.ac.uk"))
    search_path = str(cfg.get("search_path") or "/v2/objects/search")
    out_path = str(cfg.get("out_path") or "data/instruments/cache/vam_examples.jsonl")
    lock_path = str(cfg.get("lock_path") or "config/vam_collections.lock.json")
    return Pins(base_url=base_url, search_path=search_path, out_path=out_path, lock_path=lock_path)


def fetch_page(base_url: str, search_path: str, params: Dict[str, Any], timeout: int = 45) -> Dict[str, Any]:
    url = base_url.rstrip("/") + search_path
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def normalize_record(obj: Dict[str, Any], base_url: str) -> Optional[Dict[str, Any]]:
    # V&A search results typically include object_number or systemNumber.
    objnum = obj.get("object_number") or obj.get("objectNumber")
    sysnum = obj.get("systemNumber") or obj.get("system_number")
    title = obj.get("_primaryTitle") or obj.get("title") or obj.get("object")
    # Prefer systemNumber for stable linking if present.
    if sysnum:
        provider_url = f"{base_url.rstrip('/')}/v2/object/{sysnum}"
    elif objnum:
        # Not always directly resolvable, but keep for reference.
        provider_url = None
    else:
        provider_url = None
    if not (sysnum or objnum or title):
        return None
    return {
        "provider": "vam",
        "record_id": sysnum or objnum,
        "title": title,
        "provider_url": provider_url,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/vam_collections.json")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--update-lock", action="store_true")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = load_json(cfg_path)
    pins = pins_from_config(cfg)

    lock_file = Path(pins.lock_path)
    lock = load_json(lock_file) if lock_file.exists() else {}
    if args.strict and lock:
        lp = lock.get("pins") or {}
        if canonicalize_https(str(lp.get("base_url") or "")) != pins.base_url or str(lp.get("search_path") or "") != pins.search_path:
            raise RuntimeError("Pinned V&A endpoint differs from lock. Use --update-lock if intentional.")

    queries: List[Dict[str, Any]] = list(cfg.get("queries") or [])
    if not queries:
        raise RuntimeError("config.queries must be a non-empty list of parameter objects")

    rows_per_page = int(cfg.get("rows_per_page") or 45)
    max_pages = int(cfg.get("max_pages") or 5)

    out_rows: List[Dict[str, Any]] = []
    seen = set()

    for qobj in queries:
        # Each query object is merged with page/limit parameters.
        for page in range(1, max_pages + 1):
            params = dict(qobj)
            params.setdefault("page", page)
            params.setdefault("page_size", rows_per_page)
            data = fetch_page(pins.base_url, pins.search_path, params)
            records = data.get("records") or []
            if not records:
                break
            for r in records:
                nr = normalize_record(r, pins.base_url)
                if not nr:
                    continue
                key = (nr.get("record_id") or "") + "|" + (nr.get("provider_url") or "")
                if key in seen:
                    continue
                seen.add(key)
                nr["query"] = qobj
                out_rows.append(nr)

    out_path = Path(pins.out_path)
    write_jsonl(out_path, out_rows)
    out_sha = sha256_file(out_path)

    if args.update_lock or not lock_file.exists():
        write_json(
            lock_file,
            {
                "pins": {"base_url": pins.base_url, "search_path": pins.search_path},
                "output_sha256": out_sha,
            },
        )

    print(f"Wrote {len(out_rows)} V&A cached rows to {out_path} (sha256={out_sha[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

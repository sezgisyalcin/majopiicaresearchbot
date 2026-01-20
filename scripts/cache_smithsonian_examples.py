#!/usr/bin/env python3
"""Cache Smithsonian Open Access instrument examples (optional).

This script creates a lightweight local cache of museum record URLs that can be
referenced by your instrument entity registry.

Smithsonian Open Access API requires an API key obtained via api.data.gov.
Provide it via environment variable `SMITHSONIAN_API_KEY`.

This cache is OPTIONAL: the bot runs without it.

Output format: JSONL (one record per line)

Usage
-----
SMITHSONIAN_API_KEY=... python scripts/cache_smithsonian_examples.py --config config/smithsonian_openaccess.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
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
    base_url = canonicalize_https(str(cfg.get("base_url") or "https://api.si.edu"))
    search_path = str(cfg.get("search_path") or "/openaccess/api/v1.0/search")
    out_path = str(cfg.get("out_path") or "data/instruments/cache/smithsonian_examples.jsonl")
    lock_path = str(cfg.get("lock_path") or "config/smithsonian_openaccess.lock.json")
    return Pins(base_url=base_url, search_path=search_path, out_path=out_path, lock_path=lock_path)


def fetch_page(base_url: str, search_path: str, api_key: str, q: str, start: int, rows: int, timeout: int = 45) -> Dict[str, Any]:
    url = base_url.rstrip("/") + search_path
    params = {"api_key": api_key, "q": q, "start": str(start), "rows": str(rows)}
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def normalize_record(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Smithsonian search returns a variety of shapes; try to extract stable fields.
    content = row.get("content") or {}
    des = content.get("descriptiveNonRepeating") or {}
    title = des.get("title")
    record_link = des.get("record_link") or des.get("record_link")
    if not record_link:
        # Some rows expose content.record_ID; still allow caching without a URL.
        record_link = None
    record_id = content.get("id") or content.get("record_ID") or row.get("id")
    if not (record_id or record_link or title):
        return None
    return {
        "provider": "smithsonian",
        "record_id": record_id,
        "title": title,
        "provider_url": record_link,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/smithsonian_openaccess.json")
    ap.add_argument("--strict", action="store_true", help="Fail if pins differ from lock")
    ap.add_argument("--update-lock", action="store_true", help="Update lock with current pins and output sha")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = load_json(cfg_path)
    pins = pins_from_config(cfg)

    api_key = os.getenv("SMITHSONIAN_API_KEY", "").strip()
    if not api_key:
        print("SMITHSONIAN_API_KEY is required.", file=sys.stderr)
        return 2

    lock_file = Path(pins.lock_path)
    lock = load_json(lock_file) if lock_file.exists() else {}
    if args.strict and lock:
        lp = lock.get("pins") or {}
        if canonicalize_https(str(lp.get("base_url") or "")) != pins.base_url or str(lp.get("search_path") or "") != pins.search_path:
            raise RuntimeError("Pinned Smithsonian endpoint differs from lock. Use --update-lock if intentional.")

    queries: List[str] = list(cfg.get("queries") or [])
    rows_per_page = int(cfg.get("rows_per_page") or 50)
    max_rows_per_query = int(cfg.get("max_rows_per_query") or 200)
    if not queries:
        raise RuntimeError("config.queries must be a non-empty list")

    out_rows: List[Dict[str, Any]] = []
    seen = set()
    for q in queries:
        start = 0
        while start < max_rows_per_query:
            data = fetch_page(pins.base_url, pins.search_path, api_key, q, start=start, rows=rows_per_page)
            rows = (((data.get("response") or {}).get("rows")) or [])
            if not rows:
                break
            for r in rows:
                nr = normalize_record(r)
                if not nr:
                    continue
                key = (nr.get("record_id") or "") + "|" + (nr.get("provider_url") or "")
                if key in seen:
                    continue
                seen.add(key)
                nr["query"] = q
                out_rows.append(nr)
            start += rows_per_page

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

    print(f"Wrote {len(out_rows)} Smithsonian cached rows to {out_path} (sha256={out_sha[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

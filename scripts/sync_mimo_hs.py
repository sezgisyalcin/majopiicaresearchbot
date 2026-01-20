#!/usr/bin/env python3
"""Sync Hornbostel–Sachs (HS) concept cache.

This script maintains a cached HS concept file under `data/instruments/`.
It supports two modes:

1) Seed mode (default): ingest a small curated seed list (stable and offline).
2) SPARQL mode: query a configurable SKOS endpoint (e.g., MIMO thesaurus).

To keep builds deterministic and avoid silent upstream drift, the script supports
"pinning" via a config + lock pair, mirroring the UNESCO sync strategy.

Files
-----
- config/mimo_hs.json: pinned config (endpoint, mode, output paths)
- config/mimo_hs.lock.json: last-known-good pins (updated by this script)

Usage
-----
python scripts/sync_mimo_hs.py --config config/mimo_hs.json

Optional flags:
  --strict   Fail if pins differ from lock (recommended for CI)
  --update-lock  Rewrite lock to match current config (recommended for maintainers)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def canonicalize_https(url: str) -> str:
    url = (url or "").strip()
    if url.startswith("http://"):
        url = "https://" + url[len("http://") :]
    return url


def query_sparql(endpoint: str, query: str, timeout: int = 45) -> Dict[str, Any]:
    headers = {"Accept": "application/sparql-results+json"}
    resp = requests.get(endpoint, params={"query": query}, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


HS_QUERY = """
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?concept ?prefLabel ?notation WHERE {
  ?concept a skos:Concept .
  OPTIONAL { ?concept skos:prefLabel ?prefLabel . FILTER (lang(?prefLabel) = 'en') }
  OPTIONAL { ?concept skos:notation ?notation }
}
LIMIT 10000
"""


@dataclass(frozen=True)
class Pins:
    mode: str
    sparql_endpoint: str
    seed_path: str
    out_path: str


def pins_from_config(cfg: Dict[str, Any]) -> Pins:
    mode = (cfg.get("mode") or "seed").strip().lower()
    sparql_endpoint = canonicalize_https(str(cfg.get("sparql_endpoint") or ""))
    seed_path = str(cfg.get("seed_path") or "data/instruments/hs_seed.json")
    out_path = str(cfg.get("out_path") or "data/instruments/hs_concepts.json")
    return Pins(mode=mode, sparql_endpoint=sparql_endpoint, seed_path=seed_path, out_path=out_path)


def ensure_pins_valid(p: Pins) -> None:
    if p.mode not in {"seed", "sparql"}:
        raise RuntimeError("config.mode must be 'seed' or 'sparql'")
    if p.mode == "sparql" and not p.sparql_endpoint:
        raise RuntimeError("config.sparql_endpoint is required for sparql mode")


def load_lock(lock_path: Path) -> Dict[str, Any]:
    if not lock_path.exists():
        return {}
    return load_json(lock_path)


def pins_equal(p: Pins, lock: Dict[str, Any]) -> bool:
    lp = lock.get("pins") or {}
    return (
        (lp.get("mode") or "") == p.mode
        and canonicalize_https(str(lp.get("sparql_endpoint") or "")) == p.sparql_endpoint
        and str(lp.get("seed_path") or "") == p.seed_path
        and str(lp.get("out_path") or "") == p.out_path
    )


def write_lock(lock_path: Path, p: Pins, output_sha256: str) -> None:
    lock = {
        "pins": {
            "mode": p.mode,
            "sparql_endpoint": p.sparql_endpoint,
            "seed_path": p.seed_path,
            "out_path": p.out_path,
        },
        "output_sha256": output_sha256,
    }
    save_json(lock_path, lock)


def dedupe_concepts(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen = set()
    out: List[Dict[str, Any]] = []
    for c in items:
        uri = c.get("hs_uri") or c.get("concept")
        if not uri or uri in seen:
            continue
        seen.add(uri)
        out.append(
            {
                "hs_uri": uri,
                "pref_label": c.get("pref_label") or c.get("prefLabel") or c.get("label"),
                "notation": c.get("notation"),
            }
        )
    out.sort(key=lambda x: (str(x.get("notation") or ""), str(x.get("hs_uri") or "")))
    return out


def run_seed(seed_path: Path) -> List[Dict[str, Any]]:
    seed = load_json(seed_path)
    if not isinstance(seed, list):
        raise RuntimeError("Seed must be a JSON list")
    return dedupe_concepts(seed)


def run_sparql(endpoint: str) -> List[Dict[str, Any]]:
    data = query_sparql(endpoint, HS_QUERY)
    bindings = (((data.get("results") or {}).get("bindings")) or [])
    items: List[Dict[str, Any]] = []
    for b in bindings:
        uri = (b.get("concept") or {}).get("value")
        label = (b.get("prefLabel") or {}).get("value")
        notation = (b.get("notation") or {}).get("value")
        if not uri:
            continue
        items.append({"hs_uri": uri, "pref_label": label, "notation": notation})
    return dedupe_concepts(items)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config/mimo_hs.json", help="Path to config JSON")
    ap.add_argument("--lock", default="config/mimo_hs.lock.json", help="Path to lock JSON")
    ap.add_argument("--strict", action="store_true", help="Fail if config pins differ from lock")
    ap.add_argument("--update-lock", action="store_true", help="Update lock pins to match config")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    lock_path = Path(args.lock)
    cfg = load_json(cfg_path)
    p = pins_from_config(cfg)
    ensure_pins_valid(p)

    lock = load_lock(lock_path)
    if args.strict and lock and not pins_equal(p, lock):
        raise RuntimeError(
            "Pinned config differs from lock. If intentional, run with --update-lock, commit lock, and re-run CI."
        )

    # Execute
    if p.mode == "seed":
        concepts = run_seed(Path(p.seed_path))
    else:
        concepts = run_sparql(p.sparql_endpoint)

    out_obj = {"items": concepts, "meta": {"mode": p.mode, "sparql_endpoint": p.sparql_endpoint or None}}
    out_bytes = (json.dumps(out_obj, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    out_path = Path(p.out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out_bytes)

    out_sha = sha256_bytes(out_bytes)
    if args.update_lock or not lock_path.exists():
        write_lock(lock_path, p, out_sha)
    print(f"Wrote {len(concepts)} HS concepts to {out_path} (sha256={out_sha[:12]}...)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

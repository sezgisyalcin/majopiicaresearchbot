#!/usr/bin/env python3
"""Sync Hornbostel–Sachs concept cache from MIMO vocabulary.

This script maintains a small cached file (`data/instruments/hs_concepts.json`) so that
bot responses can link to stable HS concept URIs.

Approach
--------
MIMO exposes its vocabularies as SKOS and provides a SPARQL endpoint.
Because endpoint URLs can change, this script is configurable:
- You can pass --sparql-endpoint to query HS concepts.
- Or pass --seed to ingest a small manual list of HS concepts.

The default behavior is conservative: it will only run if you pass at least one of
--sparql-endpoint or --seed.

Usage
-----
# Option A: seed file
python scripts/sync_mimo_hs.py --seed data/instruments/hs_seed.json --out data/instruments/hs_concepts.json

# Option B: SPARQL (example)
python scripts/sync_mimo_hs.py --sparql-endpoint "https://example.org/sparql" --out data/instruments/hs_concepts.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, List, Optional

import requests


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


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
LIMIT 5000
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/instruments/hs_concepts.json")
    ap.add_argument("--seed", default=None, help="Path to a seed JSON file containing HS concepts")
    ap.add_argument("--sparql-endpoint", default=None, help="MIMO (or equivalent) SPARQL endpoint")
    args = ap.parse_args()

    concepts: List[Dict[str, Any]] = []

    if args.seed:
        seed = load_json(args.seed)
        if isinstance(seed, list):
            concepts.extend(seed)
        else:
            raise RuntimeError("Seed must be a JSON list")

    if args.sparql_endpoint:
        data = query_sparql(args.sparql_endpoint, HS_QUERY)
        bindings = (((data.get("results") or {}).get("bindings")) or [])
        for b in bindings:
            uri = (b.get("concept") or {}).get("value")
            label = (b.get("prefLabel") or {}).get("value")
            notation = (b.get("notation") or {}).get("value")
            if not uri:
                continue
            concepts.append({"hs_uri": uri, "pref_label": label, "notation": notation})

    if not concepts:
        print("Nothing to do. Provide --seed and/or --sparql-endpoint.", file=sys.stderr)
        return 2

    # De-duplicate by URI
    seen = set()
    deduped = []
    for c in concepts:
        uri = c.get("hs_uri") or c.get("concept")
        if not uri or uri in seen:
            continue
        seen.add(uri)
        deduped.append(c)

    save_json(args.out, {"items": sorted(deduped, key=lambda x: str(x.get("notation") or x.get("hs_uri")))})
    print(f"Wrote {len(deduped)} HS concepts to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
import os
from typing import Any, Dict, Iterable, Set

from core.source_audit import classify_source

def _walk(obj: Any) -> Iterable[Any]:
    if isinstance(obj, dict):
        for v in obj.values():
            yield v
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield v
            yield from _walk(v)

def extract_urls_from_json(data: Any) -> Set[str]:
    urls: Set[str] = set()
    for v in _walk(data):
        if isinstance(v, str) and v.startswith("http"):
            urls.add(v.strip())
    return urls

def build_registry(data_dir: str) -> Dict[str, Any]:
    urls: Set[str] = set()
    for root, _, files in os.walk(data_dir):
        for fn in files:
            if not fn.lower().endswith(".json"):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    data = json.load(f)
                urls |= extract_urls_from_json(data)
            except Exception:
                continue

    domains: Dict[str, Dict[str, Any]] = {}
    from urllib.parse import urlparse
    for u in sorted(urls):
        try:
            host = urlparse(u).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
        except Exception:
            host = ""
        if not host:
            continue
        typ = classify_source(u)
        entry = domains.setdefault(host, {"domain": host, "type": typ, "example_urls": []})
        if len(entry["example_urls"]) < 3:
            entry["example_urls"].append(u)

    by_type: Dict[str, int] = {}
    for d in domains.values():
        by_type[d["type"]] = by_type.get(d["type"], 0) + 1

    return {
        "version": "1.0.0",
        "generated_from": "data/*.json (recursive)",
        "counts": {"domains": len(domains), "urls": len(urls)},
        "by_type": dict(sorted(by_type.items(), key=lambda x: (-x[1], x[0]))),
        "domains": list(domains.values()),
    }

def write_registry(data_dir: str, out_path: str) -> Dict[str, Any]:
    reg = build_registry(data_dir)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reg, f, ensure_ascii=False, indent=2)
    return reg

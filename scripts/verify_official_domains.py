#!/usr/bin/env python3
"""Verify 'official-only' Japan brand registry entries.

The bot will only surface Japan brand records that are:
- is_active == True
- verification.status == "PASS"

This script performs automated checks to support maintainers. It is NOT a substitute
for human review.

Checks
------
- https scheme
- URL resolves (2xx)
- Captures redirect chain (final URL)
- Optional lightweight text check: presence of brand/company tokens

Usage
-----
python scripts/verify_official_domains.py \
  --registry data/japan_brands_official_registry.json \
  --report data/jp_brands_verification_report.json

Optionally:
  --timeout 20
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Tuple

import requests


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, obj: Any) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def normalize_https(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return url
    if url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url


def fetch(url: str, timeout: int) -> Tuple[str, int, List[str], str]:
    """Return (final_url, status_code, redirect_chain, body_snippet)."""
    headers = {
        "User-Agent": "majopiica-researchbot-verifier/1.0 (+https://example.invalid)"
    }
    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    chain = [h.url for h in resp.history] + [resp.url]
    text = resp.text or ""
    snippet = re.sub(r"\s+", " ", text)[:2000]
    return resp.url, resp.status_code, chain, snippet


def token_hit(snippet: str, tokens: List[str]) -> bool:
    if not snippet:
        return False
    s = snippet.lower()
    for t in tokens:
        t2 = (t or "").strip().lower()
        if len(t2) >= 3 and t2 in s:
            return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", default="data/japan_brands_official_registry.json")
    ap.add_argument("--report", default="data/jp_brands_verification_report.json")
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()

    reg = load_json(args.registry)
    items: List[Dict[str, Any]] = reg.get("items", []) if isinstance(reg, dict) else []

    results = []
    for item in items:
        brand = item.get("brand_name")
        url = normalize_https(item.get("official_url", ""))
        is_active = item.get("is_active") is True

        status = "FAIL"
        notes: List[str] = []
        final_url = ""
        code = None
        chain: List[str] = []
        text_hit = None

        if not url:
            notes.append("missing official_url")
        elif not url.startswith("https://"):
            notes.append("official_url is not https")
        else:
            try:
                final_url, code, chain, snippet = fetch(url, args.timeout)
                if code and 200 <= int(code) < 400:
                    status = "PASS"
                else:
                    notes.append(f"HTTP status {code}")
                # Lightweight content token check
                tokens = [brand, item.get("parent_company")]
                text_hit = token_hit(snippet, [t for t in tokens if t])
                if text_hit is False:
                    notes.append("token check did not match (non-fatal)")
            except Exception as e:
                notes.append(f"request failed: {e}")

        # Store result
        results.append(
            {
                "brand_name": brand,
                "official_url": url,
                "is_active": is_active,
                "final_url": final_url,
                "http_status": code,
                "redirect_chain": chain,
                "token_hit": text_hit,
                "status": status if is_active else "INACTIVE",
                "notes": notes,
            }
        )

        # Also update item.verification (non-destructive)
        item.setdefault("verification", {})
        item["verification"].update(
            {
                "status": status if is_active else "INACTIVE",
                "verified_at": reg.get("generated_at") or None,
                "final_url": final_url,
                "http_status": code,
            }
        )

    save_json(args.report, {"items": results})
    save_json(args.registry, reg)

    passes = sum(1 for r in results if r.get("status") == "PASS")
    print(f"Verification complete. PASS={passes}/{len(results)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _load_json(path: Path) -> Any:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def _save_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def _iter_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def _norm(s: str) -> str:
    s = (s or '').strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def _extract_text(rec: Dict[str, Any], fields: List[str]) -> str:
    parts: List[str] = []
    for k in fields:
        v = rec.get(k)
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, list):
            parts.append(" ".join(str(x) for x in v if x is not None))
        elif v is not None:
            parts.append(str(v))
    return _norm(" ".join(parts))


def _build_entity_keywords(entity: Dict[str, Any], min_len: int) -> List[str]:
    keys: List[str] = []
    name = entity.get('common_name') or ''
    if isinstance(name, str):
        keys.append(name)
    inst_id = entity.get('instrument_id') or ''
    if isinstance(inst_id, str) and '_' in inst_id:
        keys.extend(inst_id.split('_'))
    hs_code = entity.get('hs_code') or ''
    if isinstance(hs_code, str) and hs_code:
        keys.append(hs_code)
    # normalize and prune
    out: List[str] = []
    seen = set()
    for k in keys:
        nk = _norm(k)
        nk = re.sub(r"[^a-z0-9\.\- ]+", "", nk)
        nk = nk.strip()
        if len(nk) < min_len:
            continue
        if nk in seen:
            continue
        seen.add(nk)
        out.append(nk)
    return out


def _score_match(text: str, keywords: List[str]) -> int:
    score = 0
    for kw in keywords:
        if not kw:
            continue
        if kw in text:
            # prefer full-word-ish matches
            score += 5
            if re.search(rf"\b{re.escape(kw)}\b", text):
                score += 3
    return score


def _select_examples(
    records: List[Dict[str, Any]],
    keywords: List[str],
    fields: List[str],
    provider: str,
    max_n: int,
) -> List[Dict[str, Any]]:
    scored: List[tuple[int, Dict[str, Any]]] = []
    for r in records:
        txt = _extract_text(r, fields)
        sc = _score_match(txt, keywords)
        if sc <= 0:
            continue
        scored.append((sc, r))
    scored.sort(key=lambda t: (-t[0], _norm(str(t[1].get('title','')))))

    out: List[Dict[str, Any]] = []
    seen_urls = set()
    for sc, r in scored:
        url = (r.get('provider_url') or r.get('url') or '').strip()
        if url and url in seen_urls:
            continue
        if url:
            seen_urls.add(url)
        out.append({
            "provider": provider,
            "title": r.get('title') or r.get('name') or r.get('object_title') or "Museum record",
            "url": url,
            "image_url": (r.get('image_url') or '').strip() or None,
            "license": (r.get('license') or r.get('rights') or '').strip() or None,
        })
        if len(out) >= max_n:
            break
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Merge Smithsonian/V&A example caches into instrument_entities.json examples[].")
    ap.add_argument('--config', default='config/instrument_examples_merge.json')
    ap.add_argument('--strict', action='store_true', help='Fail if configured files are missing (except caches).')
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    cfg = _load_json(root / args.config)

    entities_path = root / cfg['entities_path']
    if not entities_path.exists():
        raise SystemExit(f"entities file not found: {entities_path}")

    smith_path = root / cfg['smithsonian_cache_jsonl']
    vam_path = root / cfg['vam_cache_jsonl']

    max_per = int(cfg.get('max_examples_per_provider', 2))
    max_total = int(cfg.get('max_total_examples', 5))
    fields = list(cfg.get('match_fields') or ['title','description','keywords','hs_code'])
    min_len = int(cfg.get('keyword_min_length', 3))

    entities = _load_json(entities_path)
    items: List[Dict[str, Any]] = entities.get('items') or []

    smith_records: List[Dict[str, Any]] = []
    if smith_path.exists() and smith_path.stat().st_size > 0:
        smith_records = list(_iter_jsonl(smith_path))

    vam_records: List[Dict[str, Any]] = []
    if vam_path.exists() and vam_path.stat().st_size > 0:
        vam_records = list(_iter_jsonl(vam_path))

    if args.strict:
        # caches are allowed to be missing; scripts that create them are optional.
        pass

    updated = 0
    for ent in items:
        keywords = _build_entity_keywords(ent, min_len=min_len)
        new_examples: List[Dict[str, Any]] = []

        if smith_records:
            new_examples.extend(_select_examples(smith_records, keywords, fields, 'smithsonian', max_per))
        if vam_records:
            new_examples.extend(_select_examples(vam_records, keywords, fields, 'vam', max_per))

        # Add any existing examples that are not duplicates, up to max_total
        existing = ent.get('examples') or []
        if isinstance(existing, list):
            for ex in existing:
                if not isinstance(ex, dict):
                    continue
                url = (ex.get('url') or '').strip()
                if url and any((e.get('url') or '') == url for e in new_examples):
                    continue
                new_examples.append(ex)

        # Dedup + trim
        seen = set()
        compact: List[Dict[str, Any]] = []
        for ex in new_examples:
            url = (ex.get('url') or '').strip()
            key = url or json.dumps(ex, sort_keys=True, ensure_ascii=False)
            if key in seen:
                continue
            seen.add(key)
            compact.append(ex)
            if len(compact) >= max_total:
                break

        if compact != (ent.get('examples') or []):
            ent['examples'] = compact
            updated += 1

    entities['items'] = items
    _save_json(entities_path, entities)
    print(f"Updated {updated} instrument entities. Caches present: smithsonian={bool(smith_records)}, vam={bool(vam_records)}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

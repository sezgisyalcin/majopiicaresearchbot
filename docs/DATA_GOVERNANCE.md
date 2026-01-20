# Data Governance (Official / Academic Sources)

This repository uses **local registries** (JSON/JSONL) that are sourced from **official** and/or **academic** reference points.

## Objectives

- Ensure each bot response includes at least one authoritative source.
- Keep runtime fast and resilient by avoiding live scraping during commands.
- Provide repeatable, reviewable data updates through scripts.

## UNESCO WHC pinning strategy (config + CI)

UNESCO data sync is designed to be stable and auditable.

- Configuration lives in `config/unesco_whc.json`.
- A lock file `config/unesco_whc.lock.json` is updated by the sync script.
- In **strict** pinning mode, CI will fail if the endpoint or `resource_id` change unexpectedly.

Operationally:
1. Set a **fixed** `ckan_datastore_search_url` (CKAN action endpoint).
2. Set the **resource UUID** in `resource_id`.
3. Run `python scripts/sync_unesco_whc001.py --config config/unesco_whc.json`.
4. Let GitHub Actions (`.github/workflows/sync_unesco_whc.yml`) update the JSONL and open a pull request.

## Registry Types

### 1) UNESCO World Heritage (WHC) JSONL
- File: `data/whc/whc_sites.jsonl`
- One JSON object per line.
- Canonical human-facing source: WHC pages on `whc.unesco.org`.
- Machine-readable source: UNESCO Datahub dataset `whc001` (recommended).

### 2) Instruments (Hornbostel–Sachs + museum examples)
- File: `data/instruments/instrument_entities.json`
- Optional: `data/instruments/hs_concepts.json` (cached concept labels/URIs)
- Concept authority: Hornbostel–Sachs classification via MIMO vocabulary.
- Example authorities: museum/collection records (Smithsonian Open Access, V&A Collections, MIMO).

### 3) Japan Brands (Official-only)
- File: `data/japan_brands_official_registry.json`
- The bot will only pick records with:
  - `is_active: true`
  - `verification.status: "PASS"`
- Each record must have exactly one **official producer / company** URL.

## Update Workflow

1. Run sync/verification scripts in `scripts/`.
2. Review diffs and verification reports.
3. Commit updated registries.
4. Deploy.

## Non-goals

- This project does not attempt to provide a complete real-time mirror of third-party databases.
- This project does not scrape content during command execution.

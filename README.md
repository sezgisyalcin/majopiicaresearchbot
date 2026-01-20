# Majopiica Research Bot (Discord)

Run:
- Set DISCORD_TOKEN
- pip install -r requirements.txt
- python main.py

Commands: /heritage random, /chocolate random, /japanbrands random, /instrument random

## Data model extensions (official/academic)

This repo supports extended, governance-driven registries:

1. **UNESCO World Heritage (ID-based JSONL)**
   - If `data/whc/whc_sites.jsonl` exists, `/heritage random` will prefer it.
   - Populate it via:
     - Edit `config/unesco_whc.json` and set the pinned `resource_id` (CKAN resource UUID)
     - Run: `python scripts/sync_unesco_whc001.py --config config/unesco_whc.json`
   - Optional: enable scheduled CI sync with `.github/workflows/sync_unesco_whc.yml`.

2. **Instruments (Hornbostel–Sachs + museum examples)**
   - If `data/instruments/instrument_entities.json` exists, `/instrument random` will prefer it.
   - Optional HS concept cache via: `python scripts/sync_mimo_hs.py --seed data/instruments/hs_seed.json`

3. **Japan brands (strict official-only)**
   - If `data/japan_brands_official_registry.json` exists, `/japanbrands random` will only pick entries with:
     - `is_active: true`
     - `verification.status: "PASS"`
   - Automated verification helper:
     - `python scripts/verify_official_domains.py --registry data/japan_brands_official_registry.json`

See `docs/DATA_GOVERNANCE.md` and `docs/DATA_SOURCES.md`.

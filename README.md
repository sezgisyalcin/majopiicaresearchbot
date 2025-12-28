

## Deploy on Railway
1. Push this repo to GitHub
2. Railway -> New Project -> Deploy from GitHub Repo
3. Add Variables:
   - TWITCH_OAUTH_TOKEN = oauth:xxxxx (from the bot account)
   - TWITCH_CHANNEL = yourchannel (no #)
   - GLOBAL_COOLDOWN_S = 2 (optional)
   - USER_COOLDOWN_S = 12 (optional)
   - CMD_COOLDOWN_S = 2 (optional)
4. Redeploy.

## Quick test in Twitch chat
- !help
- !examples
- !fashion representation
- !desserts
- !weather Rome

## Content management (no code needed)
- `data/registry.yaml`: allowlisted domains + source catalogs
- `data/packs/`: curated cards (optional). If a card is missing, commands fall back to links-only.

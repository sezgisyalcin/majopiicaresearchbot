# Academic Twitch Bot (Railway-ready)

English-only Twitch chat bot built around an **Academic/Institutional links-only** policy.
No Wikipedia/Wikidata/DBpedia links are allowed.

## Deploy on Railway
1. Push this repo to GitHub
2. Railway -> New Project -> Deploy from GitHub Repo
3. Add Variables:
   - TWITCH_OAUTH_TOKEN = oauth:xxxxx (from the bot account)
   - TWITCH_CHANNEL = yourchannel (no #)
   - GLOBAL_COOLDOWN_S = 2 (optional)
   - USER_COOLDOWN_S = 12 (optional)
   - CMD_COOLDOWN_S = 2 (optional)

### Optional: !clip command (Helix)
If you set the variables below, the bot will support `!clip` (mods/broadcaster only) and will create a Twitch clip via Helix.

Required:
- TWITCH_CLIENT_ID
- TWITCH_USER_ACCESS_TOKEN (a *user token* with scope `clips:edit` authorized for the broadcaster)
- TWITCH_BROADCASTER_ID (numeric)

### Optional: Discord bridge (post clips to Discord)
If you set the variables below, created clip URLs will also be posted to a Discord channel.

- DISCORD_TOKEN
- POST_CLIPS_TO_DISCORD=true
- DISCORD_CLIP_CHANNEL_ID (numeric)
4. Redeploy.

## Quick test in Twitch chat
- !help
- !examples
- !clip
- !fashion representation
- !desserts
- !weather Rome

## Content management (no code needed)
- `data/registry.yaml`: allowlisted domains + source catalogs
- `data/packs/`: curated cards (optional). If a card is missing, commands fall back to links-only.

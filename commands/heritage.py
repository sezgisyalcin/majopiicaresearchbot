from __future__ import annotations

import os
from pathlib import Path

import discord
from discord import app_commands

from services.embed_factory import entry_embed
from services.random_picker import pick_random_jsonl, pick_random
from services.registry_loader import load_registry_items
from utils.rate_limit import RateLimiter


def register_heritage(tree: app_commands.CommandTree, data_dir: str, limiter: RateLimiter) -> None:
    # Fallback curated registry
    curated_path = os.path.join(data_dir, "heritage_registry.json")
    # Optional: UNESCO WHC dataset (JSONL) synced via scripts/sync_unesco_whc001.py
    whc_jsonl = os.path.join(data_dir, "whc", "whc_sites.jsonl")

    group = app_commands.Group(name="heritage", description="Random curated cultural & natural heritage")

    @group.command(name="random", description="Get a random cultural/natural heritage entry (with official sources)")
    async def random_heritage(interaction: discord.Interaction) -> None:
        try:
            limiter.check(f"heritage:{interaction.user.id}")

            if os.path.exists(whc_jsonl):
                # Prefer official UNESCO WHC-derived dataset when available.
                entry = pick_random_jsonl(
                    Path(whc_jsonl),
                    predicate=lambda o: bool(o.get("whc_url")) and bool(o.get("name")),
                )
                # Normalize to embed format expected by entry_embed
                entry = {
                    "name": entry.get("name"),
                    "description": (
                        f"**State Party:** {entry.get('country') or 'Unknown'}\n"
                        f"**Category:** {entry.get('category') or 'Unknown'}\n"
                        f"**Year inscribed:** {entry.get('year_inscribed') or 'Unknown'}\n"
                        f"**Criteria:** {', '.join(entry.get('criteria', []) or []) or 'Unknown'}"
                    ),
                    "sources": [{"label": "UNESCO WHC (official)", "url": entry.get("whc_url")}],
                }
            else:
                items = load_registry_items(Path(curated_path), "items")
                entry = pick_random(items)

            emb = entry_embed("Heritage", entry)
            await interaction.response.send_message(embed=emb)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    tree.add_command(group)

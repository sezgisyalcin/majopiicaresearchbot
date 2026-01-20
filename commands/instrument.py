from __future__ import annotations

import os
from pathlib import Path

import discord
from discord import app_commands

from services.embed_factory import entry_embed
from services.random_picker import pick_random
from services.registry_loader import load_registry_items
from utils.rate_limit import RateLimiter


def register_instrument(tree: app_commands.CommandTree, data_dir: str, limiter: RateLimiter) -> None:
    legacy_path = os.path.join(data_dir, "instrument_registry.json")
    # Optional: category-based model (Hornbostel–Sachs + museum examples)
    entities_path = os.path.join(data_dir, "instruments", "instrument_entities.json")

    group = app_commands.Group(name="instrument", description="Random musical instrument (academic sources)")

    @group.command(name="random", description="Get a random musical instrument (academic / museum sources)")
    async def random_instrument(interaction: discord.Interaction) -> None:
        try:
            limiter.check(f"instrument:{interaction.user.id}")
            if os.path.exists(entities_path):
                items = load_registry_items(Path(entities_path), "items")
                reg = pick_random(items)
                # Normalize to the embed schema expected by entry_embed
                entry = {
                    "name": reg.get("common_name") or reg.get("name"),
                    "description": reg.get("short_description") or reg.get("description") or "",
                    "sources": reg.get("sources", []),
                }
                # Append HS classification + museum examples as additional fields
                hs_code = reg.get("hs_code")
                hs_uri = reg.get("hs_uri")
                examples = reg.get("examples", [])
                extra_lines = []
                if hs_code:
                    extra_lines.append(f"**Hornbostel–Sachs:** {hs_code}")
                if hs_uri:
                    entry.setdefault("sources", []).append({"label": "HS concept (MIMO)", "url": hs_uri})
                if examples:
                    # Keep examples brief; official links are in sources
                    extra_lines.append(f"**Museum examples:** {len(examples)} record(s)")
                    # Promote up to 3 example links into sources
                    for ex in examples[:3]:
                        if ex.get("provider_url"):
                            entry.setdefault("sources", []).append(
                                {"label": f"{ex.get('provider','museum').title()} record", "url": ex.get("provider_url")}
                            )
                if extra_lines:
                    entry["description"] = (entry.get("description") + "\n\n" + "\n".join(extra_lines)).strip()
            else:
                items = load_registry_items(Path(legacy_path), "items")
                entry = pick_random(items)
            emb = entry_embed("Instrument", entry)
            await interaction.response.send_message(embed=emb)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    tree.add_command(group)

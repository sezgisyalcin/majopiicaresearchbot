from __future__ import annotations

import os
from pathlib import Path

import discord
from discord import app_commands

import random

from services.embed_factory import entry_embed
from services.registry_loader import load_json, load_registry_items
from services.verification import filter_verified_official_items
from services.random_picker import pick_random
from utils.rate_limit import RateLimiter


def register_japanbrands(tree: app_commands.CommandTree, data_dir: str, limiter: RateLimiter) -> None:
    legacy_path = os.path.join(data_dir, "japan_only_food_registry.json")
    # Optional: strict official-only registry with verification metadata
    official_path = os.path.join(data_dir, "japan_brands_official_registry.json")

    group = app_commands.Group(name="japanbrands", description="Random Japan-only food/drink brands")

    @group.command(name="random", description="Get a random Japan-only food/drink brand (official sources)")
    async def random_japan_brand(interaction: discord.Interaction) -> None:
        try:
            limiter.check(f"japanbrands:{interaction.user.id}")
            if os.path.exists(official_path):
                reg = load_json(Path(official_path))
                items = filter_verified_official_items(reg)
                if not items:
                    raise RuntimeError("Official registry is present but has no PASS + active items.")
                picked = pick_random(items)
                entry = {
                    "name": picked.get("brand_name"),
                    "description": (picked.get("description") or "").strip(),
                    "sources": [{"label": "Official site", "url": picked.get("official_url")}],
                }
            else:
                items = load_registry_items(Path(legacy_path), "items")
                entry = pick_random(items)
            emb = entry_embed("Japan Brand", entry)
            await interaction.response.send_message(embed=emb)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    tree.add_command(group)

from __future__ import annotations

import os
from pathlib import Path

import discord
from discord import app_commands

from services.embed_factory import entry_embed
from services.random_picker import pick_random
from services.registry_loader import load_registry_items
from utils.rate_limit import RateLimiter


def register_chocolate(tree: app_commands.CommandTree, data_dir: str, limiter: RateLimiter) -> None:
    reg_path = os.path.join(data_dir, "europe_chocolate_registry.json")

    group = app_commands.Group(name="chocolate", description="Random European chocolate brand")

    @group.command(name="random", description="Get a random European chocolate brand (official sources)")
    async def random_chocolate(interaction: discord.Interaction) -> None:
        try:
            limiter.check(f"chocolate:{interaction.user.id}")
            items = load_registry_items(Path(reg_path), "items")
            entry = pick_random(items)
            emb = entry_embed("Chocolate", entry)
            await interaction.response.send_message(embed=emb)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    tree.add_command(group)

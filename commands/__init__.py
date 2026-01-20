from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands as dcommands

from commands.heritage import register_heritage
from commands.chocolate import register_chocolate
from commands.japanbrands import register_japanbrands
from commands.instrument import register_instrument
from commands.console_history import register_history_of_the_consoles
from commands.early_games import register_first_and_early_games_from_the_history
from commands.legacy_suite import register_legacy_suite
from utils.rate_limit import RateLimiter


def register_all_commands(bot: dcommands.Bot, tree: app_commands.CommandTree, data_dir: str, limiter: RateLimiter) -> None:
    """Register all bot commands.

    Keep main.py minimal by concentrating command wiring here.
    """
    register_heritage(tree, data_dir, limiter)
    register_chocolate(tree, data_dir, limiter)
    register_japanbrands(tree, data_dir, limiter)
    register_instrument(tree, data_dir, limiter)

    # Additional curated modules (renamed; no Bottany naming retained)
    register_history_of_the_consoles(bot, data_dir)
    register_first_and_early_games_from_the_history(bot, data_dir)

    # Legacy suite: previously developed commands migrated into this repo.
    register_legacy_suite(bot, data_dir)


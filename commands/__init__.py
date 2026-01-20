from __future__ import annotations

from discord import app_commands

from commands.heritage import register_heritage
from commands.chocolate import register_chocolate
from commands.japanbrands import register_japanbrands
from commands.instrument import register_instrument
from utils.rate_limit import RateLimiter


def register_all_commands(tree: app_commands.CommandTree, data_dir: str, limiter: RateLimiter) -> None:
    """Register all bot commands.

    Keep main.py minimal by concentrating command wiring here.
    """
    register_heritage(tree, data_dir, limiter)
    register_chocolate(tree, data_dir, limiter)
    register_japanbrands(tree, data_dir, limiter)
    register_instrument(tree, data_dir, limiter)


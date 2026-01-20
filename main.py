from __future__ import annotations

import os
import sys

import discord
from discord.ext import commands
from dotenv import load_dotenv

from commands import register_all_commands
from utils.rate_limit import RateLimiter


def main() -> None:
    load_dotenv()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN is not set.", file=sys.stderr)
        sys.exit(1)

    data_dir = os.getenv("DATA_DIR", "data")

    intents = discord.Intents.none()
    bot = commands.Bot(command_prefix="!", intents=intents)

    limiter = RateLimiter(cooldown_seconds=int(os.getenv("COOLDOWN_SECONDS", "8")))

    register_all_commands(bot, bot.tree, data_dir, limiter)

    @bot.event
    async def on_ready() -> None:
        guild_id = os.getenv("GUILD_ID")
        try:
            if guild_id:
                guild = discord.Object(id=int(guild_id))
                synced = await bot.tree.sync(guild=guild)
                print(f"Synced {len(synced)} commands to guild {guild_id}.")
            else:
                synced = await bot.tree.sync()
                print(f"Synced {len(synced)} commands globally.")
        except Exception as e:
            print(f"Command sync failed: {e}", file=sys.stderr)

        print(f"Logged in as {bot.user} (id={bot.user.id})")

    bot.run(token)


if __name__ == "__main__":
    main()

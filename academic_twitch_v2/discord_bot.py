import os
from typing import Optional

import discord

from core.logging import log


DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
POST_CLIPS_TO_DISCORD = os.getenv("POST_CLIPS_TO_DISCORD", "false").strip().lower() in {"1", "true", "yes", "y"}

_CLIP_CHANNEL_ID_RAW = os.getenv("DISCORD_CLIP_CHANNEL_ID", "").strip()
DISCORD_CLIP_CHANNEL_ID: Optional[int]
try:
    DISCORD_CLIP_CHANNEL_ID = int(_CLIP_CHANNEL_ID_RAW) if _CLIP_CHANNEL_ID_RAW else None
except Exception:
    DISCORD_CLIP_CHANNEL_ID = None


class DiscordBridge(discord.Client):
    """Minimal Discord client used as an outbound notification bridge."""

    def __init__(self):
        intents = discord.Intents.none()
        super().__init__(intents=intents)

    async def on_ready(self):
        log("discord_ready", user=str(self.user))

    async def post_clip(self, clip_url: str, *, twitch_channel: str, requested_by: str) -> None:
        if not POST_CLIPS_TO_DISCORD:
            return
        if not DISCORD_CLIP_CHANNEL_ID:
            return
        channel = self.get_channel(DISCORD_CLIP_CHANNEL_ID)
        if channel is None:
            # Lazy-fetch if needed
            try:
                channel = await self.fetch_channel(DISCORD_CLIP_CHANNEL_ID)
            except Exception:
                return
        if not isinstance(channel, (discord.TextChannel, discord.Thread)):
            return

        msg = f"New clip from Twitch channel '{twitch_channel}' (requested by {requested_by}):\n{clip_url}"
        await channel.send(msg)


def is_discord_configured() -> bool:
    return bool(DISCORD_TOKEN)


async def start_discord_bridge() -> DiscordBridge:
    """Start Discord client and return it once connected."""
    bridge = DiscordBridge()
    await bridge.login(DISCORD_TOKEN)
    # connect() blocks until closed; we need it running in a background task.
    return bridge

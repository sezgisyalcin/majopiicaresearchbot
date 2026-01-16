import asyncio
import os

from dotenv import load_dotenv

from bot import create_twitch_bot
from discord_bot import DiscordBridge, is_discord_configured, DISCORD_TOKEN


load_dotenv()


async def main() -> None:
    discord_bridge = None

    discord_task = None
    if is_discord_configured():
        discord_bridge = DiscordBridge()
        discord_task = asyncio.create_task(discord_bridge.start(DISCORD_TOKEN))

    async def _discord_clip_poster(clip_url: str, ctx) -> None:
        if discord_bridge is None:
            return
        twitch_channel = os.getenv("TWITCH_CHANNEL", "")
        requested_by = getattr(ctx.author, "name", "unknown")
        await discord_bridge.post_clip(clip_url, twitch_channel=twitch_channel, requested_by=requested_by)

    twitch_bot = create_twitch_bot(discord_clip_poster=_discord_clip_poster if discord_bridge else None)
    twitch_task = asyncio.create_task(twitch_bot.start())

    tasks = [twitch_task]
    if discord_task is not None:
        tasks.append(discord_task)

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())

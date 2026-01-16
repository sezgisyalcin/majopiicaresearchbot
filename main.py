
import asyncio
from bot import create_twitch_bot
from discord_bot import create_discord_bot

async def main():
    twitch_bot = create_twitch_bot()
    discord_bot = create_discord_bot()
    await asyncio.gather(
        twitch_bot.start(),
        discord_bot.start(os.getenv("DISCORD_TOKEN"))
    )

if __name__ == "__main__":
    import os
    asyncio.run(main())

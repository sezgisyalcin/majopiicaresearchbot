
from twitchio.ext import commands
from utils.logger import log
import os

logger = log("twitch")

def create_twitch_bot():
    return Bot()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=os.getenv("TWITCH_BOT_OAUTH_TOKEN"),
            prefix="!",
            initial_channels=[os.getenv("TWITCH_CHANNEL")]
        )

    async def event_ready(self):
        logger.info("Twitch bot ready")

    @commands.command(name="clip")
    async def clip(self, ctx):
        await ctx.send("Clip command active")

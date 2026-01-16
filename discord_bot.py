
import discord
from utils.logger import log

logger = log("discord")

class DiscordBot(discord.Client):
    async def on_ready(self):
        logger.info("Discord bot ready")

def create_discord_bot():
    intents = discord.Intents.default()
    return DiscordBot(intents=intents)

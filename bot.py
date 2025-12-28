import os, time
from dotenv import load_dotenv
from twitchio.ext import commands

from core.logging import log
from core.rate_limit import RL
from core.http_health import start_health_server

from commands.basic import cmd_help, cmd_examples, cmd_sources
from commands.fashion import cmd_fashion
from commands.cuisine import cmd_cuisine, cmd_alcohol, cmd_icecream, cmd_desserts, cmd_fermentation
from commands.linguistics import cmd_italianphonology, cmd_italianlinguistics, cmd_languageandbrain
from commands.weather import cmd_weather, cmd_metservice

load_dotenv()

TOKEN = os.getenv("TWITCH_OAUTH_TOKEN", "").strip()
CHANNEL = os.getenv("TWITCH_CHANNEL", "").strip()

GLOBAL_COOLDOWN = int(os.getenv("GLOBAL_COOLDOWN_S", "2"))
USER_COOLDOWN = int(os.getenv("USER_COOLDOWN_S", "12"))
CMD_COOLDOWN = int(os.getenv("CMD_COOLDOWN_S", "2"))

if not TOKEN or not CHANNEL:
    raise SystemExit("Missing TWITCH_OAUTH_TOKEN or TWITCH_CHANNEL environment variables.")

class AcademicBot(commands.Bot):
    def __init__(self):
        super().__init__(token=TOKEN, prefix="!", initial_channels=[CHANNEL])

    async def event_ready(self):
        start_health_server()
        log("bot_ready", nick=self.nick, channel=CHANNEL)

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    async def _ok(self, ctx, cmd_name: str) -> bool:
        return RL.allow(user=ctx.author.name, cmd=cmd_name,
                        user_cooldown_s=USER_COOLDOWN, cmd_cooldown_s=CMD_COOLDOWN, global_cooldown_s=GLOBAL_COOLDOWN)

    @commands.command(name="help")
    async def _help(self, ctx):
        if not await self._ok(ctx, "help"): return
        await cmd_help(ctx)

    @commands.command(name="examples")
    async def _examples(self, ctx):
        if not await self._ok(ctx, "examples"): return
        await cmd_examples(ctx)

    @commands.command(name="sources")
    async def _sources(self, ctx):
        if not await self._ok(ctx, "sources"): return
        topic = ctx.message.content.replace("!sources", "").strip()
        await cmd_sources(ctx, topic)

    @commands.command(name="fashion")
    async def _fashion(self, ctx):
        if not await self._ok(ctx, "fashion"): return
        sub = ctx.message.content.replace("!fashion", "").strip()
        await cmd_fashion(ctx, sub)

    @commands.command(name="cuisine")
    async def _cuisine(self, ctx):
        if not await self._ok(ctx, "cuisine"): return
        topic = ctx.message.content.replace("!cuisine", "").strip()
        await cmd_cuisine(ctx, topic)

    @commands.command(name="alcohol")
    async def _alcohol(self, ctx):
        if not await self._ok(ctx, "alcohol"): return
        await cmd_alcohol(ctx)

    @commands.command(name="icecream")
    async def _icecream(self, ctx):
        if not await self._ok(ctx, "icecream"): return
        await cmd_icecream(ctx)

    @commands.command(name="desserts")
    async def _desserts(self, ctx):
        if not await self._ok(ctx, "desserts"): return
        await cmd_desserts(ctx)

    @commands.command(name="fermentation")
    async def _fermentation(self, ctx):
        if not await self._ok(ctx, "fermentation"): return
        await cmd_fermentation(ctx)

    @commands.command(name="italianphonology")
    async def _italianphonology(self, ctx):
        if not await self._ok(ctx, "italianphonology"): return
        await cmd_italianphonology(ctx)

    @commands.command(name="italianlinguistics")
    async def _italianlinguistics(self, ctx):
        if not await self._ok(ctx, "italianlinguistics"): return
        await cmd_italianlinguistics(ctx)

    @commands.command(name="languageandbrain")
    async def _languageandbrain(self, ctx):
        if not await self._ok(ctx, "languageandbrain"): return
        await cmd_languageandbrain(ctx)

    @commands.command(name="weather")
    async def _weather(self, ctx):
        if not await self._ok(ctx, "weather"): return
        city = ctx.message.content.replace("!weather", "").strip()
        await cmd_weather(ctx, city)

    @commands.command(name="metservice")
    async def _metservice(self, ctx):
        if not await self._ok(ctx, "metservice"): return
        country = ctx.message.content.replace("!metservice", "").strip()
        await cmd_metservice(ctx, country)

bot = AcademicBot()
bot.run()

import os
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

# Optional Discord bridge + Helix clip creation support
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID", "").strip()
TWITCH_USER_ACCESS_TOKEN = os.getenv("TWITCH_USER_ACCESS_TOKEN", "").strip()
TWITCH_BROADCASTER_ID = os.getenv("TWITCH_BROADCASTER_ID", "").strip()

GLOBAL_COOLDOWN = int(os.getenv("GLOBAL_COOLDOWN_S", "2"))
USER_COOLDOWN = int(os.getenv("USER_COOLDOWN_S", "12"))
CMD_COOLDOWN = int(os.getenv("CMD_COOLDOWN_S", "2"))

if not TOKEN or not CHANNEL:
    raise SystemExit("Missing TWITCH_OAUTH_TOKEN or TWITCH_CHANNEL environment variables.")

def _has_clip_env() -> bool:
    return bool(TWITCH_CLIENT_ID and TWITCH_USER_ACCESS_TOKEN and TWITCH_BROADCASTER_ID)

class AcademicBot(commands.Bot):
    def __init__(self, *, discord_clip_poster=None):
        """Twitch chat bot.

        Parameters
        ----------
        discord_clip_poster:
            Optional async callable (clip_url: str, ctx) -> None
            If provided, created clip URLs will be posted to Discord.
        """
        super().__init__(token=TOKEN, prefix="!", initial_channels=[CHANNEL])
        self._discord_clip_poster = discord_clip_poster

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

    @commands.command(name="clip")
    async def _clip(self, ctx):
        """Create a Twitch clip for the current channel (mods/broadcaster only).

        Requirements:
        - TWITCH_CLIENT_ID
        - TWITCH_USER_ACCESS_TOKEN (user token with scope clips:edit)
        - TWITCH_BROADCASTER_ID (numeric)
        """
        if not await self._ok(ctx, "clip"):
            return

        # Permission gate: mods or broadcaster
        is_mod = bool(getattr(ctx.author, "is_mod", False))
        is_broadcaster = bool(getattr(ctx.author, "is_broadcaster", False))
        if not (is_mod or is_broadcaster):
            await ctx.send("Only mods or the broadcaster can create clips.")
            return

        if not _has_clip_env():
            await ctx.send("Clip feature is not configured on the server (missing Helix env vars).")
            return

        from services.twitch_clips import create_clip

        try:
            clip_url = await create_clip(
                broadcaster_id=TWITCH_BROADCASTER_ID,
                client_id=TWITCH_CLIENT_ID,
                user_access_token=TWITCH_USER_ACCESS_TOKEN,
            )
        except Exception:
            await ctx.send("Could not create a clip right now. Please try again.")
            return

        await ctx.send(f"Clip created: {clip_url}")

        if self._discord_clip_poster is not None:
            try:
                await self._discord_clip_poster(clip_url, ctx)
            except Exception:
                # Never fail the Twitch command because of Discord
                pass

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

def create_twitch_bot(*, discord_clip_poster=None) -> AcademicBot:
    return AcademicBot(discord_clip_poster=discord_clip_poster)


if __name__ == "__main__":
    bot = create_twitch_bot()
    bot.run()

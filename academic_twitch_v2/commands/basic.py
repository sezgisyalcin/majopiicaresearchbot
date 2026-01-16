from core.policy import clamp
from commands.common import links_message

async def cmd_help(ctx):
    msg = (
        "Commands: !help | !examples | !sources <topic> | "
        "!fashion <journals|museums|archives|theory|representation|sustainability|economics|technology|materials|law|colonialism> | "
        "!cuisine <topic> | !alcohol | !icecream | !desserts | !fermentation | "
        "!italianphonology | !italianlinguistics | !languageandbrain | "
        "!weather <city> | !metservice <country>"
    )
    await ctx.send(clamp(msg))

async def cmd_examples(ctx):
    msg = (
        "Examples: !sources fashion_journals | !fashion representation | !desserts | "
        "!italianphonology | !weather Rome | !metservice Italy"
    )
    await ctx.send(clamp(msg))

async def cmd_sources(ctx, topic: str):
    if not topic:
        await ctx.send("Usage: !sources <topic>. Example: !sources fashion_journals")
        return
    await ctx.send(links_message(f"{topic} (academic/institutional links)", topic, limit=8))

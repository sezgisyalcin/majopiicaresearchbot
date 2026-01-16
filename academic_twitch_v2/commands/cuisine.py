from commands.common import links_message

async def cmd_cuisine(ctx, topic: str):
    topic = (topic or "").strip()
    if not topic:
        await ctx.send("Usage: !cuisine <topic>. Example: !cuisine pasta")
        return
    await ctx.send(links_message(f"Italian cuisine / gastronomy (academic links) — topic: {topic}", "cuisine_general", limit=8))

async def cmd_alcohol(ctx):
    await ctx.send(links_message("Alcohol studies (fermentation / wine / spirits) — academic links", "cuisine_alcohol", limit=8))

async def cmd_icecream(ctx):
    await ctx.send(links_message("Ice cream / frozen desserts — food science academic links", "cuisine_icecream", limit=8))

async def cmd_desserts(ctx):
    await ctx.send(links_message("Desserts & pastry — academic links", "cuisine_desserts", limit=8))

async def cmd_fermentation(ctx):
    await ctx.send(links_message("Fermentation (microbiology & culture) — academic links", "cuisine_fermentation", limit=8))

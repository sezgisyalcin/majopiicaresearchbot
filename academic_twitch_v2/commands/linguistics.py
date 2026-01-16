from commands.common import links_message

async def cmd_italianphonology(ctx):
    await ctx.send(links_message("Italian phonology (academic links)", "italian_phonology", limit=8))

async def cmd_italianlinguistics(ctx):
    await ctx.send(links_message("Italian linguistics (academic links)", "italian_linguistics", limit=8))

async def cmd_languageandbrain(ctx):
    await ctx.send(links_message("Language & brain (neurolinguistics) — academic links", "language_and_brain", limit=8))

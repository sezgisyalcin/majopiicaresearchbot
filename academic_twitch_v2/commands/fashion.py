from commands.common import links_message

FASHION_TOPICS = {
    "journals": ("Fashion journals (OA / selected OA)", "fashion_journals"),
    "museums": ("Fashion museums & research archives", "fashion_museums"),
    "archives": ("Fashion digitized archives & libraries", "fashion_archives"),
    "theory": ("Fashion theory & critical studies", "fashion_theory"),
    "representation": ("Fashion representation & visual culture", "fashion_representation"),
    "sustainability": ("Sustainable fashion & circular textiles", "fashion_sustainability"),
    "economics": ("Fashion economics, labor, supply chains", "fashion_economics"),
    "technology": ("Fashion technology & smart textiles", "fashion_technology"),
    "materials": ("Textile/materials science", "fashion_materials"),
    "law": ("Fashion law & IP", "fashion_law"),
    "colonialism": ("Decolonial/postcolonial fashion studies", "fashion_colonialism"),
}

async def cmd_fashion(ctx, subtopic: str):
    subtopic = (subtopic or "").strip().lower()
    if subtopic not in FASHION_TOPICS:
        await ctx.send("Usage: !fashion <journals|museums|archives|theory|representation|sustainability|economics|technology|materials|law|colonialism>")
        return
    label, key = FASHION_TOPICS[subtopic]
    await ctx.send(links_message(label, key, limit=8))



# ---- Embed support ----

async def post_clip_embed(self, clip_url: str, title: str, broadcaster: str):
    if not self.clip_channel:
        return
    embed = discord.Embed(
        title=title or "New Twitch Clip",
        url=clip_url,
        description=f"New clip from **{broadcaster}**",
        color=0x9146FF
    )
    embed.add_field(name="Watch Clip", value=clip_url, inline=False)
    embed.set_footer(text="Bottany Twitch Bridge")
    await self.clip_channel.send(embed=embed)

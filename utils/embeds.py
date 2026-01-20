from __future__ import annotations

from typing import Any, Dict, List

import discord


def entry_embed(title_prefix: str, entry: Dict[str, Any]) -> discord.Embed:
    """Create a consistent embed for registry items."""
    name = entry.get("name", "Unknown")
    e = discord.Embed(title=f"{title_prefix}: {name}")

    subtitle = entry.get("subtitle") or entry.get("type") or entry.get("category")
    if subtitle:
        e.description = str(subtitle)

    description = entry.get("description")
    if description:
        e.add_field(name="Summary", value=str(description), inline=False)

    meta_bits: List[str] = []
    for key in ("country", "region", "period", "classification"):
        val = entry.get(key)
        if val:
            meta_bits.append(f"{key.title()}: {val}")
    if meta_bits:
        e.add_field(name="Metadata", value="\n".join(meta_bits), inline=False)

    sources = entry.get("sources") or []
    if isinstance(sources, str):
        sources = [sources]
    if sources:
        shown = sources[:3]
        e.add_field(name="Official / Academic sources", value="\n".join(shown), inline=False)

    note = entry.get("note")
    if note:
        e.set_footer(text=str(note))

    return e

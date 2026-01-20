from __future__ import annotations

from typing import Any, Dict, List

import discord


def _format_sources(sources: Any) -> List[str]:
    """Normalize sources into a list of displayable strings."""
    if not sources:
        return []
    if isinstance(sources, str):
        return [sources]

    out: List[str] = []
    if isinstance(sources, list):
        for s in sources:
            if isinstance(s, str):
                out.append(s)
            elif isinstance(s, dict):
                label = (s.get("label") or "Source").strip()
                url = (s.get("url") or "").strip()
                if url:
                    out.append(f"{label}: {url}")
            else:
                # Fallback: string cast
                out.append(str(s))
    else:
        out.append(str(sources))
    return out


def entry_embed(title_prefix: str, entry: Dict[str, Any]) -> discord.Embed:
    """Create a consistent embed for registry items.

    This is a service-layer version that tolerates richer 'sources' shapes.
    """
    name = entry.get("name", "Unknown")
    e = discord.Embed(title=f"{title_prefix}: {name}")

    subtitle = entry.get("subtitle") or entry.get("type") or entry.get("category")
    if subtitle:
        e.description = str(subtitle)

    description = entry.get("description")
    if description:
        e.add_field(name="Summary", value=str(description), inline=False)

    meta_bits: List[str] = []
    for key in ("country", "region", "period", "classification", "hs_code"):
        val = entry.get(key)
        if val:
            meta_bits.append(f"{key.replace('_', ' ').title()}: {val}")
    if meta_bits:
        e.add_field(name="Metadata", value="\n".join(meta_bits), inline=False)

    sources = _format_sources(entry.get("sources"))
    if sources:
        e.add_field(name="Official / Academic sources", value="\n".join(sources[:3]), inline=False)

    note = entry.get("note")
    if note:
        e.set_footer(text=str(note))

    return e

from __future__ import annotations

from typing import Any

async def ensure_public_send(interaction: Any, content: str | None = None, **kwargs) -> None:
    if "ephemeral" not in kwargs:
        kwargs["ephemeral"] = False
    await interaction.response.send_message(content=content, **kwargs)

async def ensure_followup_public(interaction: Any, content: str | None = None, **kwargs) -> None:
    if "ephemeral" not in kwargs:
        kwargs["ephemeral"] = False
    await interaction.followup.send(content=content, **kwargs)

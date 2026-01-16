import aiohttp


HELIX_BASE = "https://api.twitch.tv/helix"


async def create_clip(*, broadcaster_id: str, client_id: str, user_access_token: str) -> str:
    """Create a Twitch clip via Helix.

    Notes
    -----
    - `user_access_token` must be a *user token* (not an app token) that is
      authorized for the target broadcaster and includes the `clips:edit` scope.
    """
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {user_access_token}",
    }
    params = {"broadcaster_id": broadcaster_id}

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{HELIX_BASE}/clips", headers=headers, params=params) as resp:
            data = await resp.json(content_type=None)
            if resp.status >= 300:
                raise RuntimeError(f"Helix error {resp.status}: {data}")

    items = (data or {}).get("data") or []
    if not items or not items[0].get("edit_url"):
        raise RuntimeError(f"Unexpected Helix response: {data}")

    # edit_url is the canonical URL returned by Helix for freshly created clips
    return items[0]["edit_url"]

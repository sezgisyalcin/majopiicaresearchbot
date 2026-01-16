import aiohttp
from bs4 import BeautifulSoup
from cachetools import TTLCache

MEMBERS_CACHE = TTLCache(maxsize=1, ttl=24*3600)

async def _get_html(url: str) -> str:
    headers = {"User-Agent": "academic-twitch-bot/1.0"}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers, timeout=25) as r:
            r.raise_for_status()
            return await r.text()

async def load_members(members_url: str) -> dict[str, str]:
    if "members" in MEMBERS_CACHE:
        return MEMBERS_CACHE["members"]
    html = await _get_html(members_url)
    soup = BeautifulSoup(html, "lxml")
    members = {}
    for a in soup.select("table a[href]"):
        name = a.get_text(" ", strip=True)
        href = a.get("href", "")
        if name and href and len(name) >= 3:
            members[name.lower()] = href
    MEMBERS_CACHE["members"] = members
    return members

async def get_member_link(members_url: str, country_query: str) -> str | None:
    members = await load_members(members_url)
    q = country_query.lower().strip()
    for k, v in members.items():
        if q in k:
            return v
    return None

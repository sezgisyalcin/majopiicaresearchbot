from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import asyncio, json, os, time
import aiohttp

# Note: endpoints are fetched live at request time.
# Epic endpoint is a public store backend JSON used by the Epic Games Store frontend.
EPIC_FREE_PROMOS = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"
GOG_FILTERED = "https://www.gog.com/games/ajax/filtered"

REGION_TO_COUNTRY_LOCALE = {
    "global": ("US", "en-US"),
    "us": ("US", "en-US"),
    "uk": ("GB", "en-GB"),
    # EU is not a single storefront country; use a stable English locale with a major EU country code.
    "eu": ("DE", "en-GB"),
}

@dataclass(frozen=True)
class FreeGameItem:
    platform: str
    title: str
    url: str
    start: Optional[str] = None  # ISO-ish
    end: Optional[str] = None
    raw_id: Optional[str] = None

def _now_ms() -> int:
    return int(time.time() * 1000)

async def _get_json(session: aiohttp.ClientSession, url: str, params: Dict[str, str], timeout_s: int = 20) -> Any:
    async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=timeout_s)) as r:
        r.raise_for_status()
        return await r.json()

async def fetch_epic_free_games(region: str = "global") -> List[FreeGameItem]:
    country, locale = REGION_TO_COUNTRY_LOCALE.get(region, REGION_TO_COUNTRY_LOCALE["global"])
    params = {"locale": locale, "country": country, "allowCountries": country}
    async with aiohttp.ClientSession(headers={"User-Agent": "AcademicDiscordBot/1.0"}) as session:
        data = await _get_json(session, EPIC_FREE_PROMOS, params=params)
    catalog = (data or {}).get("data") or {}
    catalog = catalog.get("Catalog") or {}
    search = (catalog.get("searchStore") or {})
    elements = search.get("elements") or []
    out: List[FreeGameItem] = []
    for el in elements:
        promos = (el.get("promotions") or {})
        promo_list = (promos.get("promotionalOffers") or [])
        if not promo_list:
            continue
        # Identify if current promo is 0 price; Epic marks discountPercentage=0 sometimes; safest: presence in free promotions endpoint is already filtered.
        # We still guard by offerType and dates.
        title = el.get("title") or "Untitled"
        slug = el.get("productSlug") or el.get("urlSlug") or ""
        url = f"https://store.epicgames.com/{locale}/p/{slug}" if slug else "https://store.epicgames.com/"
        # Current promotional offer window (first)
        offer = (promo_list[0].get("promotionalOffers") or [{}])[0]
        start = offer.get("startDate")
        end = offer.get("endDate")
        raw_id = el.get("id") or el.get("namespace")
        out.append(FreeGameItem("Epic", title, url, start=start, end=end, raw_id=raw_id))
    return out

async def fetch_gog_free_games(page: int = 1) -> List[FreeGameItem]:
    params = {
        "mediaType": "game",
        "price": "free",
        "page": str(page),
        "sort": "popularity",
    }
    async with aiohttp.ClientSession(headers={"User-Agent": "AcademicDiscordBot/1.0"}) as session:
        data = await _get_json(session, GOG_FILTERED, params=params)
    products = (data or {}).get("products") or []
    out: List[FreeGameItem] = []
    for p in products:
        title = p.get("title") or "Untitled"
        slug = p.get("slug") or ""
        url = f"https://www.gog.com/en/game/{slug}" if slug else "https://www.gog.com/en/"
        raw_id = str(p.get("id") or slug)
        out.append(FreeGameItem("GOG", title, url, raw_id=raw_id))
    return out

def load_seen(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"seen": {}}

def save_seen(path: str, payload: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def mark_new(items: List[FreeGameItem], seen: Dict[str, Any]) -> Tuple[List[FreeGameItem], Dict[str, Any]]:
    s = (seen or {}).get("seen") or {}
    new: List[FreeGameItem] = []
    for it in items:
        key = f"{it.platform}:{it.raw_id or it.title}"
        if key not in s:
            new.append(it)
            s[key] = {"t": _now_ms(), "title": it.title, "url": it.url}
    seen["seen"] = s
    return new, seen

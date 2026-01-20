from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

MICHELIN_BASE = "https://guide.michelin.com"
DEFAULT_LOCALE = "en"

TERRITORY_MAP: Dict[str, str] = {
    "global": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/restaurants",
    "italy": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/it/restaurants",
    "france": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/fr/restaurants",
    "uk": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/gb/restaurants",
    "ireland": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/ie/restaurants",
    "usa": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/us/restaurants",
    "japan": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/jp/restaurants",
    "turkey": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/tr/restaurants",
    "germany": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/de/restaurants",
    "spain": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/es/restaurants",
    "portugal": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/pt/restaurants",
    "netherlands": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/nl/restaurants",
    "belgium": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/be/restaurants",
    "switzerland": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/ch/restaurants",
    "austria": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/at/restaurants",
    "sweden": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/se/restaurants",
    "norway": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/no/restaurants",
    "denmark": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/dk/restaurants",
    "singapore": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/sg/restaurants",
    "thailand": f"{MICHELIN_BASE}/{DEFAULT_LOCALE}/th/restaurants",
}

AWARD_PATH_MAP: Dict[str, str] = {
    "3-star": "3-stars-michelin",
    "2-star": "2-stars-michelin",
    "1-star": "1-star-michelin",
    "bib": "bib-gourmand",
    "selected": "the-plate-michelin",
}

@dataclass
class MichelinRestaurant:
    name: str
    location: str
    cuisine: str
    price: str
    award: str
    url: str

def _cache_dir(base_dir: str) -> str:
    d = os.path.join(base_dir, ".cache", "michelin")
    os.makedirs(d, exist_ok=True)
    return d

def _cache_key(territory: str, award: str, page: int, city: Optional[str], cuisine: Optional[str]) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_\-]+", "_", f"{territory}_{award}_{page}_{city or ''}_{cuisine or ''}".strip())
    return safe.lower() + ".json"

def _get_text(el) -> str:
    return " ".join(el.get_text(" ", strip=True).split()) if el else ""

def _parse_restaurant_cards(html: str) -> List[MichelinRestaurant]:
    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.card__menu-content") or soup.select("div.card__content")
    results: List[MichelinRestaurant] = []
    for card in cards:
        a = card.select_one("a.link") or card.select_one("h3 a") or card.select_one("a")
        name = _get_text(a) or _get_text(card.select_one("h3"))
        href = a.get("href") if a else None
        if not name or not href:
            continue
        url = href if href.startswith("http") else MICHELIN_BASE + href

        loc = _get_text(card.select_one("div.card__menu-footer--location")) or _get_text(card.select_one("div.card__menu-footer"))
        meta = _get_text(card.select_one("div.card__menu-footer--price"))

        cuisine = ""
        price = ""
        if "·" in meta:
            parts = [p.strip() for p in meta.split("·", 1)]
            price = parts[0] if parts else ""
            cuisine = parts[1] if len(parts) > 1 else ""

        award = ""
        parent = card.parent
        if parent:
            pt = _get_text(parent)
            if "3 Stars" in pt:
                award = "3-star"
            elif "2 Stars" in pt:
                award = "2-star"
            elif "1 Star" in pt:
                award = "1-star"
            elif "Bib Gourmand" in pt:
                award = "bib"
            elif "Selected Restaurants" in pt:
                award = "selected"

        results.append(MichelinRestaurant(name=name, location=loc, cuisine=cuisine, price=price, award=award, url=url))

    uniq = {}
    for r in results:
        uniq[r.url] = r
    return list(uniq.values())

def fetch_restaurants(base_dir: str, territory: str, award: str = "selected", page: int = 1,
                     city: Optional[str] = None, cuisine: Optional[str] = None,
                     ttl_seconds: int = 21600) -> List[MichelinRestaurant]:
    territory_key = (territory or "").strip().lower()
    if territory_key not in TERRITORY_MAP:
        raise ValueError("Unknown territory")

    award_key = (award or "selected").strip().lower()
    if award_key not in AWARD_PATH_MAP and award_key != "any":
        raise ValueError("Unknown award")

    url = TERRITORY_MAP[territory_key].rstrip("/")

    if award_key in AWARD_PATH_MAP:
        url = url + "/" + AWARD_PATH_MAP[award_key]

    if page and page > 1:
        url = url + f"/page/{int(page)}"

    cache_path = os.path.join(_cache_dir(base_dir), _cache_key(territory_key, award_key, int(page or 1), city, cuisine))
    now = time.time()
    if os.path.exists(cache_path):
        try:
            cached = json.load(open(cache_path, "r", encoding="utf-8"))
            if now - cached.get("ts", 0) <= ttl_seconds:
                return [MichelinRestaurant(**it) for it in cached.get("items", [])]
        except Exception:
            pass

    headers = {"User-Agent": "Mozilla/5.0 (compatible; AcademicBot/1.0; +https://guide.michelin.com/)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()

    items = _parse_restaurant_cards(resp.text)

    if city:
        c = city.strip().lower()
        items = [i for i in items if c in (i.location or "").lower() or c in (i.name or "").lower()]
    if cuisine:
        cu = cuisine.strip().lower()
        items = [i for i in items if cu in (i.cuisine or "").lower()]

    json.dump({"ts": now, "url": url, "items": [i.__dict__ for i in items]}, open(cache_path, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    return items

def michelin_explain_urls(locale: str = "en") -> Dict[str, str]:
    base = f"{MICHELIN_BASE}/{locale}"
    return {
        "michelin_star": f"{base}/article/features/what-is-a-michelin-star",
        "bib_gourmand": f"{base}/article/features/the-bib-gourmand",
        "green_star": f"{base}/article/features/what-is-the-michelin-green-star",
    }

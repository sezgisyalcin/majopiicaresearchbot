import aiohttp
from rapidfuzz import process, fuzz
from core.cache import CITIES_CACHE, FORECAST_CACHE

async def _get_text(url: str) -> str:
    headers = {"User-Agent": "academic-twitch-bot/1.0"}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers, timeout=25) as r:
            r.raise_for_status()
            return await r.text()

async def _get_json(url: str) -> dict:
    headers = {"User-Agent": "academic-twitch-bot/1.0"}
    async with aiohttp.ClientSession() as s:
        async with s.get(url, headers=headers, timeout=25) as r:
            r.raise_for_status()
            return await r.json()

async def load_city_list(city_list_url: str) -> list[dict]:
    if "cities" in CITIES_CACHE:
        return CITIES_CACHE["cities"]
    raw = await _get_text(city_list_url)
    cities = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        city_id = parts[0].strip()
        city_name = parts[1].strip()
        country = parts[2].strip() if len(parts) > 2 else ""
        if city_id.isdigit() and city_name:
            cities.append({"id": city_id, "name": city_name, "country": country})
    CITIES_CACHE["cities"] = cities
    return cities

def match_city(cities: list[dict], query: str) -> dict | None:
    choices = {f"{c['name']} ({c['country']})": c for c in cities}
    best = process.extractOne(query, choices.keys(), scorer=fuzz.WRatio)
    if not best or best[1] < 78:
        return None
    return choices[best[0]]

async def get_official_city_forecast(city_list_url: str, json_template: str, query: str) -> dict | None:
    cities = await load_city_list(city_list_url)
    city = match_city(cities, query)
    if not city:
        return None
    cache_key = city["id"]
    if cache_key in FORECAST_CACHE:
        return FORECAST_CACHE[cache_key]
    url = json_template.format(city_id=city["id"])
    data = await _get_json(url)

    city_name = (data.get("city") or {}).get("cityName") or city["name"]
    member = (data.get("member") or {}).get("memberName") or city["country"]

    forecast_days = ((data.get("forecast") or {}).get("forecastDay") or [])
    summary = []
    for day in forecast_days[:2]:
        summary.append({
            "date": day.get("forecastDate", ""),
            "wx": day.get("wxDesc", "") or day.get("wx", ""),
            "tmax": day.get("forecastMaxtemp", ""),
            "tmin": day.get("forecastMintemp", ""),
        })

    result = {
        "matched": f"{city['name']} ({city['country']})",
        "city": city_name,
        "member": member,
        "source_url": url,
        "summary": summary,
    }
    FORECAST_CACHE[cache_key] = result
    return result

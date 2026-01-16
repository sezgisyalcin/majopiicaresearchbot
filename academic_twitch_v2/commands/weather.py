from core.registry import REG
from core.policy import clamp
from sources.wwis_weather import get_official_city_forecast
from sources.wwis_members import get_member_link

async def cmd_weather(ctx, city: str):
    if not city:
        await ctx.send("Usage: !weather <city>. Example: !weather Rome")
        return
    wwis = REG.get("weather", "wwis", default={}) or {}
    result = await get_official_city_forecast(wwis["city_list_url"], wwis["json_url_template"], city)
    if not result:
        await ctx.send("City not found in the official WMO WWIS city list. Try a major city name.")
        return
    parts = []
    for d in result["summary"]:
        parts.append(f"{d['date']}: {d['wx']} (min {d['tmin']}°C / max {d['tmax']}°C)")
    summary = " | ".join(parts) if parts else "Forecast available at the source."
    await ctx.send(clamp(
        f"Matched: {result['matched']}. Official forecast for {result['city']} (provider: {result['member']}): {summary} | Source: {result['source_url']}"
    ))

async def cmd_metservice(ctx, country: str):
    if not country:
        await ctx.send("Usage: !metservice <country>. Example: !metservice Italy")
        return
    members_url = REG.get("weather", "wwis", "members_url")
    url = await get_member_link(members_url, country)
    if not url:
        await ctx.send("No matching national meteorological service found in the WMO WWIS member list.")
        return
    await ctx.send(clamp(f"Official meteorological service link for '{country}': {url} (via WMO WWIS members list)"))

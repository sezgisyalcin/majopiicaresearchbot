from __future__ import annotations
import os
import requests

DEFAULT_TIMEOUT = 12

def _ua() -> str:
    # Official APIs (e.g., api.met.no, api.weather.gov) expect a descriptive User-Agent.
    return os.getenv("WEATHER_USER_AGENT") or "AcademicDiscordBot/1.0 (contact: set WEATHER_USER_AGENT)"

def nws_now(lat: float, lon: float) -> dict:
    """US NWS: fetch nearest gridpoint and return first forecast period + observation links."""
    headers = {"User-Agent": _ua(), "Accept": "application/geo+json, application/json"}
    p = requests.get(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}", headers=headers, timeout=DEFAULT_TIMEOUT)
    p.raise_for_status()
    pj = p.json()
    forecast_url = pj.get("properties", {}).get("forecast")
    forecast_hourly_url = pj.get("properties", {}).get("forecastHourly")
    if not forecast_url:
        raise RuntimeError("NWS points response missing forecast URL.")
    f = requests.get(forecast_url, headers=headers, timeout=DEFAULT_TIMEOUT)
    f.raise_for_status()
    fj = f.json()
    periods = (fj.get("properties", {}) or {}).get("periods", []) or []
    first = periods[0] if periods else {}
    return {
        "provider": "NOAA National Weather Service (NWS)",
        "forecast_period": first,
        "links": {
            "points": p.url,
            "forecast": forecast_url,
            "forecastHourly": forecast_hourly_url,
        },
    }

def metno_now(lat: float, lon: float) -> dict:
    """MET Norway Locationforecast: return current instant details (first timeseries item)."""
    headers = {"User-Agent": _ua(), "Accept": "application/json"}
    url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat:.4f}&lon={lon:.4f}"
    r = requests.get(url, headers=headers, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    j = r.json()
    ts = ((j.get("properties") or {}).get("timeseries") or [])
    first = ts[0] if ts else {}
    return {
        "provider": "MET Norway (Locationforecast 2.0)",
        "timeseries": first,
        "links": {"endpoint": url},
    }


def wwis_city_link(city: str) -> str:
    """WMO WWIS city search (official national service forecasts for selected cities)."""
    from urllib.parse import quote_plus
    return f"https://worldweather.wmo.int/en/search.html?keyword={quote_plus(city)}"

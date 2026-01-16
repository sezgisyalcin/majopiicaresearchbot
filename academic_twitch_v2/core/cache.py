from cachetools import TTLCache
CITIES_CACHE = TTLCache(maxsize=1, ttl=24*3600)
FORECAST_CACHE = TTLCache(maxsize=2000, ttl=45*60)

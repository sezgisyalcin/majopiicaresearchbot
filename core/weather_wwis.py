from __future__ import annotations
import re
import requests

DEFAULT_TIMEOUT = 12

# Lightweight HTML parsing (no scraping of provider sites; uses WMO WWIS directory only).

def find_member_link(country_name: str, members_url: str = "https://worldweather.wmo.int/en/members.html") -> str | None:
    """Return a best-effort URL from the WMO WWIS members directory for the given country name."""
    q = (country_name or "").strip()
    if not q:
        return None

    r = requests.get(members_url, timeout=DEFAULT_TIMEOUT)
    r.raise_for_status()
    html = r.text

    # Typical pattern: <a href="...">Country</a>
    # We match case-insensitively and return the first link text match.
    pattern = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>\s*' + re.escape(q) + r'\s*</a>', re.IGNORECASE)
    m = pattern.search(html)
    if not m:
        # Fallback: partial match (country appears inside the anchor text)
        pattern2 = re.compile(r'<a[^>]+href="([^"]+)"[^>]*>\s*([^<]*' + re.escape(q) + r'[^<]*)</a>', re.IGNORECASE)
        m = pattern2.search(html)
    if not m:
        return None

    href = m.group(1).strip()
    if href.startswith('http'):
        return href
    # WWIS links are usually relative
    return 'https://worldweather.wmo.int' + href if href.startswith('/') else 'https://worldweather.wmo.int/' + href

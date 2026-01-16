from core.registry import REG
from core.policy import is_allowed, clamp

def links_for(topic: str, limit: int = 6) -> list[str]:
    allow = REG.allowlist()
    items = REG.get("sources", topic, default=[]) or []
    urls = []
    for it in items:
        u = it.get("url")
        if u and is_allowed(u, allow):
            urls.append(u)
    return urls[:limit]

def links_message(label: str, topic: str, limit: int = 6) -> str:
    urls = links_for(topic, limit=limit)
    if not urls:
        return clamp(f"No allowlisted sources configured for '{topic}'. Ask a moderator to extend data/registry.yaml.")
    return clamp(f"{label}: " + " | ".join(urls))

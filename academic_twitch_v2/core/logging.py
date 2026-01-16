import json, time, os

def log(event: str, **fields):
    redacted = {}
    for k, v in fields.items():
        if any(s in k.lower() for s in ["token", "secret", "password", "oauth"]):
            redacted[k] = "***REDACTED***"
        else:
            redacted[k] = v
    payload = {
        "ts": int(time.time()),
        "event": event,
        "service": "academic-twitch-bot",
        "env": os.getenv("RAILWAY_ENVIRONMENT", "local"),
        **redacted,
    }
    print(json.dumps(payload, ensure_ascii=False))

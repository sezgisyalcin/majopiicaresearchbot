import json, time, os
LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'audit.jsonl')
def log_event(event: dict) -> None:
    event = dict(event)
    event.setdefault('ts', int(time.time()))
    try:
        with open(LOG_PATH, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event, ensure_ascii=False)+'\n')
    except Exception:
        pass

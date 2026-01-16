import yaml
from core.logging import log

class Registry:
    def __init__(self, path="data/registry.yaml"):
        self.path = path
        self.data = {}
        self.load()

    def load(self):
        with open(self.path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f) or {}
        log("registry_loaded", path=self.path, version=self.data.get("bot", {}).get("registry_version"))

    def allowlist(self) -> set[str]:
        return set(self.data.get("allowlist_domains", []) or [])

    def get(self, *keys, default=None):
        cur = self.data
        for k in keys:
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

REG = Registry()

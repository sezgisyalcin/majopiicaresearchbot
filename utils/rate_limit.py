from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RateLimiter:
    cooldown_seconds: int = 8
    _state: Dict[str, float] = field(default_factory=dict)

    def check(self, key: str) -> None:
        """Simple in-memory rate limiter. Raises RuntimeError if called too frequently."""
        now_ts = asyncio.get_event_loop().time()
        last_ts = self._state.get(key, 0.0)
        if now_ts - last_ts < self.cooldown_seconds:
            remaining = int(self.cooldown_seconds - (now_ts - last_ts))
            raise RuntimeError(f"Rate limit: try again in {remaining}s.")
        self._state[key] = now_ts

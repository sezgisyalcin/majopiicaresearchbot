import time

class RateLimiter:
    def __init__(self):
        self.user_last = {}
        self.cmd_last = {}
        self.global_last = 0.0

    def allow(self, user: str, cmd: str, user_cooldown_s: int, cmd_cooldown_s: int, global_cooldown_s: int) -> bool:
        now = time.time()
        if now - self.global_last < global_cooldown_s:
            return False
        uk = (user, cmd)
        if uk in self.user_last and (now - self.user_last[uk]) < user_cooldown_s:
            return False
        if cmd in self.cmd_last and (now - self.cmd_last[cmd]) < cmd_cooldown_s:
            return False
        self.global_last = now
        self.user_last[uk] = now
        self.cmd_last[cmd] = now
        return True

RL = RateLimiter()

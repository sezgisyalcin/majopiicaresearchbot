import time
class TTLCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self._store = {}
    def get(self, key):
        item = self._store.get(key)
        if not item: return None
        value, exp = item
        if time.time() > exp:
            self._store.pop(key, None)
            return None
        return value
    def set(self, key, value):
        self._store[key] = (value, time.time()+self.ttl)
    def stats(self):
        return {'size': len(self._store), 'ttl': self.ttl}

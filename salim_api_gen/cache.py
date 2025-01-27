import time
from typing import Dict, Any


class APICache:
    def __init__(self, ttl: int = 300):
        self.cache: Dict[str, Any] = {}
        self.ttl = ttl

    def get(self, key: str) -> Any:
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = (value, time.time())

import json
import time
from typing import Any
from backend.app.core.config import get_settings


class Cache:
    def __init__(self):
        self._memory: dict[str, tuple[float, Any]] = {}
        self._redis = None
        try:
            import redis
            self._redis = redis.from_url(get_settings().redis_url, decode_responses=True, socket_connect_timeout=0.2)
            self._redis.ping()
        except Exception:
            self._redis = None

    async def get(self, key: str) -> Any | None:
        if self._redis:
            value = self._redis.get(key)
            return json.loads(value) if value else None
        item = self._memory.get(key)
        if not item:
            return None
        expires, value = item
        if expires < time.time():
            self._memory.pop(key, None)
            return None
        return value

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        if self._redis:
            self._redis.setex(key, ttl_seconds, json.dumps(value))
        else:
            self._memory[key] = (time.time() + ttl_seconds, value)


cache = Cache()

from typing import Any
import json
import contextlib

import orjson

from redis import ConnectionPool
import redis.asyncio as redis
from eora.config.base import Config


class AsyncCustomRedis:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                AsyncCustomRedis,
                cls,
            ).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.redis = None
            self.initialized = False
            self.pool = None

    async def initialize(self):
        if not self.initialized:
            redis_url = (
                f"redis://:{Config.REDIS_PASSWORD}"
                f"@{Config.REDIS_HOST}"
                f":{Config.REDIS_PORT}"
            )
            self.pool = redis.ConnectionPool.from_url(
                url=redis_url,
                encoding="utf-8",
                decode_responses=True,
                retry_on_timeout=True,
                max_connections=100,
            )
            self.redis = redis.Redis(connection_pool=self.pool)
            self.initialized = True

    async def get_json(self, key: str) -> Any:
        """Получение и десериализация JSON объекта по ключу."""

        value = await self.redis.get(key)
        if value is not None:
            return orjson.loads(value)
        return None

    async def set_json(self, key: str, value: Any):
        """Сериализация и сохранение объекта как JSON по ключу."""

        await self.redis.set(key, orjson.dumps(value))

    async def get(self, key, default=None):
        """Получение данных."""

        value = await self.redis.get(key)
        if value is None:
            return default

        with contextlib.suppress(Exception):
            value = orjson.loads(value)
        return value

    async def get_str(self, key: str, default: str = None):
        value = await self.redis.get(key)
        return value if value is not None else default

    async def set(self, key: str, value: str):
        """Сохранение строки напрямую"""

        await self.redis.set(key, value)

    async def close(self):
        """Завершение сеанса."""

        await self.redis.close()


redis_async = AsyncCustomRedis()

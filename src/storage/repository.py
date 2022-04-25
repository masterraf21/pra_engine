from pydantic import parse_obj_as
from src.critical_path.models import CriticalPath

import redis.asyncio as redis
from redis.commands.json.path import Path


class StorageRepository:
    def __init__(self, redis: redis.Redis) -> None:
        self._redis = redis

    async def store_json(self, key: str, data):
        return await self._redis.json().set(key, Path.root_path(), data)

    async def retrieve_durations(self, key: str) -> list[float]:
        raw = await self._redis.json().get(key)
        data = parse_obj_as(list[float], raw)
        return data

    async def retrieve_critical_path(self, key: str) -> list[CriticalPath]:
        raw = await self._redis.json().get(key)
        data = parse_obj_as(list[CriticalPath], raw)
        return data

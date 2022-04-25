import json

import aioredis
from pydantic import parse_obj_as
from src.critical_path.models import CriticalPath

import redis as rds
from redis.commands.json.path import Path


class StorageRepositoryAsync:

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def store_json(self, key: str, data: str):
        pass
        # return await self._redis.get_js


class StorageRepositorySync:
    def __init__(self, redis: rds.Redis) -> None:
        self._redis = redis

    def store_json(self, key: str, data: str):
        return self._redis.json().set(key, Path.rootPath(), data)

    def retrieve_durations(self, key: str) -> list[float]:
        raw = self._redis.json().get(key)
        data = parse_obj_as(list[float], json.loads(raw))
        return data

    def retrieve_critical_path(self, key: str) -> list[CriticalPath]:
        raw = self._redis.json().get(key)
        data = parse_obj_as(list[CriticalPath], json.loads(raw))
        return data

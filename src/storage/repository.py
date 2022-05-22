from pydantic import parse_obj_as
from src.critical_path.models import CriticalPath, PathDuration
from src.scheduling.models import GlobalState
import redis.asyncio as redis
from redis.commands.json.path import Path
import json


class StorageRepository:
    def __init__(self, redis: redis.Redis) -> None:
        self._redis = redis

    async def store_json(self, key: str, data):
        return await self._redis.json().set(key, Path.root_path(), data)

    async def update_state(self, data: GlobalState) -> None:
        return await self.store_json("state", data.json())

    async def retrieve_state(self) -> GlobalState:
        data = await self._redis.json().get("state")
        if data is None:
            return GlobalState()
        else:
            state = parse_obj_as(GlobalState, json.loads(data))
            return state

    async def retrieve_durations(self, key: str) -> list[float]:
        raw = await self._redis.json().get(key)
        data = parse_obj_as(list[float], json.loads(raw))
        return data

    async def retrieve_critical_path(self, key: str) -> list[CriticalPath]:
        raw = await self._redis.json().get(key)
        data = parse_obj_as(list[CriticalPath], json.loads(raw))
        return data

    async def retrieve_critical_path_v2(self, key: str) -> list[PathDuration]:
        raw = await self._redis.json().get(key)
        data = parse_obj_as(list[PathDuration], json.loads(raw))
        return data

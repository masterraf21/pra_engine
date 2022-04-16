import json

from critical_path.models import CriticalPath
from pydantic import parse_obj_as

from .redis import init_redis_client


def retrieve_durations(key: str) -> list[float]:
    client = init_redis_client()
    raw = client.json().get(key)
    data = parse_obj_as(list[float], json.loads(raw))
    return data


def retrieve_critical_path(key: str) -> list[CriticalPath]:
    client = init_redis_client()
    raw = client.json().get(key)
    data = parse_obj_as(list[CriticalPath], json.loads(raw))
    return data

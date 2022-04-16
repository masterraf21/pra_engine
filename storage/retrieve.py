from .redis import init_redis_client
import json


def retrieve_list(key: str) -> list[float]:
    client = init_redis_client()
    raw = client.json().get(key)
    data: list[float] = list(json.loads(raw))
    return data

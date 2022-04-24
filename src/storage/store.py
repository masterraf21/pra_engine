from redis.commands.json.path import Path

from .redis import init_redis_client


def store_json(key: str, data: str):
    client = init_redis_client()
    client.json().set(key, Path.rootPath(), data)

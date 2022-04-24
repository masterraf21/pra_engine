from pydantic import BaseModel
from redis import Redis
from storage.redis import init_redis_client


class Dependencies(BaseModel):
    redis: Redis


def init_dependencies() -> Dependencies:
    redis_client = init_redis_client()

    dep = Dependencies(
        redis=redis_client
    )
    return dep

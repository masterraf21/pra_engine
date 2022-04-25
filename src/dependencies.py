from typing import Optional

import aioredis
import redis
from pydantic import BaseModel

from storage.redis import init_redis_client, init_redis_pool


class Dependencies(BaseModel):
    redis_sync: redis.Redis
    redis_async: Optional[aioredis.Redis]


async def init_dependencies() -> Dependencies:
    redis_client = init_redis_client()
    # redis_pool = await init_redis_pool()

    dep = Dependencies(
        redis_sync=redis_client,
        # redis_async=redis_pool
    )

    return dep

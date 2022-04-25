from src import config

import redis.asyncio as redis

settings = config.Settings()


async def init_redis_pool() -> redis.Redis:
    redis_conn = await redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_response=True
    )

    return redis_conn


def init_redis_client() -> redis.Redis:
    client = redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_response=True
    )

    return client

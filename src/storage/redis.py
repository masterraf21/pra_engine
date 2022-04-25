from src.config import get_settings

import redis.asyncio as redis
settings = get_settings()


async def init_redis() -> redis.Redis:
    redis_conn = await redis.from_url(
        settings.redis_url,
        encoding="utf-8"
    )

    return redis_conn

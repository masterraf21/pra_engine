from src.config import get_settings

import redis.asyncio as redis

from src.utils.logging import get_logger
env = get_settings()
logger = get_logger(__name__)


async def init_redis() -> redis.Redis:
    redis_conn: redis.Redis = await redis.from_url(
        env.redis_url,
        encoding="utf-8"
    )
    check = await redis_conn.ping()
    if check:
        logger.info("Redis connected")
    else:
        logger.info("Redis not connected")

    return redis_conn

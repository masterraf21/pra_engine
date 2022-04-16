from config import settings

from redis import Redis

REDIS_URL = settings.redis_url


def init_redis_client():
    redis_url = str(REDIS_URL).split(":")
    if not redis_url:
        raise ValueError("NO redis url found")
    redis_host, redis_port = "localhost", 6379
    if len(redis_url) >= 1:
        redis_host = redis_url[0]
        if len(redis_url) == 2:
            redis_port = int(redis_url[1])
    client = Redis(
        host=redis_host,
        port=redis_url
    )

    return client

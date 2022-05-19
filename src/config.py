import os
from functools import lru_cache


from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: str = os.getenv("TESTING", "0")
    debug: bool = os.getenv("DEBUG", False)
    redis_url: AnyUrl = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_password: str = os.getenv("REDIS_PASSWORD", "redis_pass")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_hash: str = os.getenv("REDIS_TEST_KEY", "covid-19-test")
    zipkin_url: AnyUrl = os.getenv("ZIPKIN_URL", "http://localhost:9411/zipkin/api/v2")
    realtime_period: int = int(os.getenv("REALTIME_CHECK_PERIOD", "5"))
    alpha: float = float(os.getenv("ALPHA", "0.05"))
    scheduler: bool = os.getenv("SCHEDULER", False)
    latency_threshold = int(os.getenv("LATENCY_THRESHOLD", "250"))


@lru_cache()
def get_settings() -> Settings:
    return Settings()

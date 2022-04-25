import os
from functools import lru_cache


from pydantic import AnyUrl, BaseSettings

from src.scheduling.models import GlobalState
from src.utils.logging import get_logger

logger = get_logger(__name__)

state = GlobalState()
ALPHA = 0.05


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: str = os.getenv("TESTING", "0")
    redis_url: AnyUrl = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_password: str = os.getenv("REDIS_PASSWORD", "redis_pass")
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    redis_hash: str = os.getenv("REDIS_TEST_KEY", "covid-19-test")
    zipkin_url: AnyUrl = os.getenv("ZIPKIN_URL", "http://localhost:9411/zipkin/api/v2")


@lru_cache()
def get_settings() -> Settings:
    # logger.info("Loading config settings from the environment...")
    return Settings()

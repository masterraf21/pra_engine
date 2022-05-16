from src.config import get_settings
settings = get_settings()

REALTIME_CHECK_PERIOD = settings.realtime_period*60  # in seconds
TRACE_LIMIT = 50000

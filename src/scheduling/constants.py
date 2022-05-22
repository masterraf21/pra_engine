from src.config import get_settings
env = get_settings()

REALTIME_CHECK_PERIOD = env.realtime_period*60  # in seconds
TRACE_LIMIT = 50000

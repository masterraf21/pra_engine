from apscheduler.schedulers.asyncio import AsyncIOScheduler
from .jobs import EngineJobs
from .constants import REALTIME_CHECK_PERIOD
from src.utils.logging import get_logger

logger = get_logger(__name__)


class Scheduler:
    def __init__(self, jobs: EngineJobs) -> None:
        self._jobs = jobs
        self._sch = AsyncIOScheduler()

    def start(self):
        logger.info("Starting Scheduler")
        self._sch.start()
        self._sch.add_job(self._jobs.regression_analysis, 'interval', seconds=REALTIME_CHECK_PERIOD)
